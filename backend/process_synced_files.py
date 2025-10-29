#!/usr/bin/env python3
"""
Manual script to process already-synced Google Drive files
Run this if auto-processing during sync didn't work
"""

import sys
import json
from app.services.file_manager import file_manager
from app.services.parser import parser
from app.services.kg_builder import kg_builder
from app.services.rag_engine import rag_engine
from app.services.doc_type_detector import doc_detector
import requests
import os

def process_synced_files(user_id: str, access_token: str):
    """Process all synced Google Drive files for a user"""
    
    # Load registry
    with open('uploads/file_registry.json', 'r') as f:
        registry = json.load(f)
    
    # Find synced files for this user
    synced_files = []
    for key, file_info in registry.items():
        if file_info.get('user_id') == user_id and file_info.get('source') == 'gdrive':
            synced_files.append(file_info)
    
    print(f"Found {len(synced_files)} synced files for user {user_id}")
    
    headers = {"Authorization": f"Bearer {access_token}"}
    processed = 0
    
    for file_info in synced_files:
        file_id = file_info['file_id']
        filename = file_info['filename']
        mime_type = file_info.get('mime_type', '')
        
        print(f"\n{'='*60}")
        print(f"Processing: {filename}")
        print(f"File ID: {file_id}")
        print(f"MIME: {mime_type}")
        
        try:
            # Determine export format
            if 'spreadsheet' in mime_type:
                export_mime = 'text/csv'
                ext = '.csv'
            elif 'document' in mime_type:
                export_mime = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
                ext = '.docx'
            else:
                print(f"⚠️  Unsupported type: {mime_type}")
                continue
            
            # Download
            print(f"Downloading as {ext}...")
            response = requests.get(
                f"https://www.googleapis.com/drive/v3/files/{file_id}/export",
                headers=headers,
                params={"mimeType": export_mime},
                timeout=30
            )
            
            if response.status_code != 200:
                print(f"❌ Download failed: {response.status_code}")
                continue
            
            # Save temporarily
            temp_path = f"uploads/temp_{file_id}{ext}"
            with open(temp_path, 'wb') as f:
                f.write(response.content)
            print(f"✓ Downloaded {len(response.content)} bytes")
            
            # Parse
            print("Parsing...")
            parsed_data = parser.parse_file(temp_path)
            print(f"✓ Parsed {len(parsed_data)} records")
            
            # Detect type
            sample_content = str(parsed_data[0].get('content', ''))[:2000] if parsed_data else ""
            doc_info = doc_detector.detect_type(sample_content)
            doc_type = doc_info.get("type", "unknown")
            print(f"✓ Detected type: {doc_type}")
            
            # Build KG
            print("Building Knowledge Graph...")
            kg_result = kg_builder.build_graph(parsed_data, file_id, user_id, doc_type)
            print(f"✓ Added {kg_result.get('nodes', 0)} nodes to KG")
            
            # Store embeddings
            print("Storing embeddings...")
            rag_engine.store_embeddings(parsed_data, file_id, user_id)
            print(f"✓ Stored embeddings")
            
            # Clean up
            os.remove(temp_path)
            processed += 1
            print(f"✅ Successfully processed: {filename}")
            
        except Exception as e:
            print(f"❌ Error processing {filename}: {e}")
            import traceback
            traceback.print_exc()
    
    print(f"\n{'='*60}")
    print(f"Processed {processed}/{len(synced_files)} files")
    
    # Show final graph stats
    if user_id in kg_builder.graphs:
        G = kg_builder.graphs[user_id]
        print(f"\nFinal graph: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")
        
        file_ids = set(data.get('file_id') for _, data in G.nodes(data=True) if data.get('file_id'))
        print(f"Files in graph: {len(file_ids)}")
        for fid in file_ids:
            count = sum(1 for _, d in G.nodes(data=True) if d.get('file_id') == fid)
            print(f"  {fid}: {count} nodes")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python process_synced_files.py <user_id> <access_token>")
        print("\nExample:")
        print("  python process_synced_files.py 112944693963105753678 ya29.a0...")
        sys.exit(1)
    
    user_id = sys.argv[1]
    access_token = sys.argv[2]
    
    process_synced_files(user_id, access_token)
