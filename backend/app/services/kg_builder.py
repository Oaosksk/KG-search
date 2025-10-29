import spacy
import networkx as nx
import pickle
from pathlib import Path
from typing import List, Dict, Any
from .llm_entity_extractor import llm_extractor
from .supabase_client import supabase_client

class KGBuilder:
    def __init__(self):
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except:
            self.nlp = None
        
        self.storage_dir = Path("storage/graphs")
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.graphs = {}
    
    def extract_entities(self, text: str, use_llm: bool = True) -> List[Dict[str, Any]]:
        entities = []
        
        # Try LLM first for better extraction
        if use_llm and llm_extractor.enabled:
            try:
                llm_result = llm_extractor.extract_entities_and_relations(text)
                entities.extend(llm_result.get("entities", []))
            except:
                pass
        
        # Fallback to spaCy
        if not entities and self.nlp:
            doc = self.nlp(text)
            entities = [{"text": ent.text, "type": ent.label_, "value": ent.text} 
                       for ent in doc.ents if ent.label_ in ['ORG', 'PERSON', 'MONEY', 'PRODUCT', 'GPE', 'DATE']]
        
        return entities
    
    def build_graph(self, data: List[Dict[str, Any]], file_id: str, user_id: str, doc_type: str = "unknown"):
        if user_id not in self.graphs:
            self.graphs[user_id] = nx.Graph()
        
        G = self.graphs[user_id]
        nodes_added = 0
        
        for item in data:
            content = str(item.get('content', ''))
            
            # Try LLM extraction first, fallback to spaCy
            entities = []
            relations = []
            detected_type = doc_type
            
            if llm_extractor.enabled:
                try:
                    llm_result = llm_extractor.extract_entities_and_relations(content, doc_type)
                    entities = llm_result.get("entities", [])
                    relations = llm_result.get("relations", [])
                    detected_type = llm_result.get("doc_type", doc_type)
                except Exception as e:
                    print(f"LLM extraction failed, using spaCy: {e}")
            
            # Fallback to spaCy if LLM failed or disabled
            if not entities:
                entities = self.extract_entities(content, use_llm=False)
                detected_type = doc_type
            
            # Add nodes with normalized values
            for entity in entities:
                node_id = f"{entity['text']}_{entity['type']}"
                entity_value = entity.get("value", entity["text"])
                
                # Normalize numeric values
                if entity['type'] == 'MONEY':
                    try:
                        entity_value = str(float(str(entity_value).replace(',', '').replace('$', '')))
                    except:
                        pass
                
                G.add_node(node_id, 
                          entity_text=entity["text"], 
                          entity_type=entity["type"],
                          entity_value=entity_value,
                          file_id=file_id,
                          doc_type=detected_type,
                          metadata=item)
                nodes_added += 1
            
            # Add relations from LLM
            print(f"\n  Processing {len(entities)} entities, {len(relations)} relations")
            
            for rel in relations:
                # Find matching nodes by entity text or value
                source_node = None
                target_node = None
                
                for node_id, node_data in G.nodes(data=True):
                    entity_text = node_data.get('entity_text', '')
                    entity_value = str(node_data.get('entity_value', ''))
                    
                    if entity_text == rel['source'] or entity_value == rel['source']:
                        source_node = node_id
                    if entity_text == rel['target'] or entity_value == rel['target']:
                        target_node = node_id
                
                # If target not found, create it as a node
                if source_node and not target_node:
                    # Infer type from relation
                    target_type = 'MONEY' if 'amount' in rel['relation'] else 'DATE' if 'date' in rel['relation'] or 'on' in rel['relation'] else 'VALUE'
                    target_node = f"{rel['target']}_{target_type}"
                    G.add_node(target_node,
                              entity_text=rel['target'],
                              entity_type=target_type,
                              entity_value=rel['target'],
                              file_id=file_id,
                              doc_type=detected_type,
                              metadata=item)
                    print(f"  + Created missing node: {rel['target']} ({target_type})")
                
                if source_node and target_node:
                    G.add_edge(source_node, target_node, relation=rel['relation'])
                    print(f"  ✓ {rel['source']} --[{rel['relation']}]--> {rel['target']}")
                else:
                    if not source_node:
                        print(f"  ✗ Source not found: {rel['source']}")
                    if not target_node:
                        print(f"  ✗ Target not found: {rel['target']}")
            
            # Only add fallback relations if LLM provided none
            if not relations and entities:
                print("  ⚠️ No LLM relations, adding fallback hub structure")
                # Find hub node (ID or ORG)
                hub_node = None
                for entity in entities:
                    if entity['type'] in ['ID', 'ORG']:
                        hub_node = f"{entity['text']}_{entity['type']}"
                        if G.has_node(hub_node):
                            break
                
                if hub_node:
                    for entity in entities:
                        node = f"{entity['text']}_{entity['type']}"
                        if node != hub_node and G.has_node(node):
                            G.add_edge(hub_node, node, relation="related_to")
        
        self._save_graph(user_id)
        return {"nodes": nodes_added, "doc_type": detected_type}
    
    def query_graph(self, query: str, user_id: str) -> Dict[str, Any]:
        if user_id not in self.graphs:
            self._load_graph(user_id)
        
        if user_id not in self.graphs or len(self.graphs[user_id].nodes()) == 0:
            return {"nodes": [], "edges": []}
        
        entities = self.extract_entities(query)
        entity_texts = [e["text"].lower() for e in entities]
        
        G = self.graphs[user_id]
        
        # If no query entities, return all nodes (limited)
        if not entity_texts:
            all_nodes = list(G.nodes(data=True))[:50]
            nodes = [{"entity_text": data.get('entity_text', 'Unknown'),
                     "entity_type": data.get('entity_type', 'UNKNOWN'),
                     "entity_value": data.get('entity_value', '')} 
                    for node, data in all_nodes]
            
            edges = []
            node_ids = [n[0] for n in all_nodes]
            for i, (node, _) in enumerate(all_nodes):
                for neighbor in G.neighbors(node):
                    if neighbor in node_ids:
                        j = node_ids.index(neighbor)
                        edge_data = G.get_edge_data(node, neighbor)
                        edges.append({
                            "source": i,
                            "target": j,
                            "relation": edge_data.get('relation', 'related')
                        })
            
            return {"nodes": nodes, "edges": edges}
        
        # Find matching nodes and neighbors
        matched_nodes = []
        node_map = {}
        
        for node, data in G.nodes(data=True):
            entity_text = data.get('entity_text', '').lower()
            if any(et in entity_text for et in entity_texts):
                idx = len(matched_nodes)
                node_map[node] = idx
                matched_nodes.append((node, data))
                
                # Add neighbors
                for neighbor in G.neighbors(node):
                    if neighbor not in node_map:
                        idx = len(matched_nodes)
                        node_map[neighbor] = idx
                        matched_nodes.append((neighbor, G.nodes[neighbor]))
        
        # Build response
        nodes = [{"entity_text": data.get('entity_text', 'Unknown'),
                 "entity_type": data.get('entity_type', 'UNKNOWN'),
                 "entity_value": data.get('entity_value', '')} 
                for node, data in matched_nodes[:50]]
        
        edges = []
        for node, _ in matched_nodes[:50]:
            if node in node_map:
                for neighbor in G.neighbors(node):
                    if neighbor in node_map:
                        edge_data = G.get_edge_data(node, neighbor)
                        edges.append({
                            "source": node_map[node],
                            "target": node_map[neighbor],
                            "relation": edge_data.get('relation', 'related')
                        })
        
        return {"nodes": nodes, "edges": edges}
    
    def _save_graph(self, user_id: str):
        # Save to local file
        with open(self.storage_dir / f"{user_id}.pkl", 'wb') as f:
            pickle.dump(self.graphs[user_id], f)
        
        # Save to Supabase if enabled
        if supabase_client.enabled:
            try:
                G = self.graphs[user_id]
                for node, data in G.nodes(data=True):
                    supabase_client.client.table('kg_nodes').upsert({
                        'user_id': user_id,
                        'node_id': node,
                        'entity_text': data.get('entity_text'),
                        'entity_type': data.get('entity_type'),
                        'entity_value': data.get('entity_value'),
                        'file_id': data.get('file_id'),
                        'doc_type': data.get('doc_type'),
                        'metadata': data.get('metadata', {})
                    }).execute()
                
                for source, target, edge_data in G.edges(data=True):
                    supabase_client.client.table('kg_edges').upsert({
                        'user_id': user_id,
                        'source_node': source,
                        'target_node': target,
                        'relation': edge_data.get('relation', 'related')
                    }).execute()
                
                print(f"✅ Saved {G.number_of_nodes()} nodes and {G.number_of_edges()} edges to Supabase")
            except Exception as e:
                print(f"⚠️ Failed to save to Supabase: {e}")
    
    def _load_graph(self, user_id: str):
        graph_path = self.storage_dir / f"{user_id}.pkl"
        if graph_path.exists():
            with open(graph_path, 'rb') as f:
                self.graphs[user_id] = pickle.load(f)

kg_builder = KGBuilder()
