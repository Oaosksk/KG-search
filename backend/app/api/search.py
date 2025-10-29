from fastapi import APIRouter, Depends
from ..models.schemas import SearchRequest, SearchResponse, SearchResult, FeedbackRequest
from ..core.auth import get_current_user
from ..services.search_engine import search_engine
from ..services.answer_generator import answer_generator
from ..services.kg_builder import kg_builder
from ..services.query_analyzer import query_analyzer
from ..services.structured_query_engine import structured_query_engine
from ..services.feedback_learner import feedback_learner

router = APIRouter(prefix="/search", tags=["search"])

@router.post("/", response_model=SearchResponse)
async def search(request: SearchRequest, user: dict = Depends(get_current_user)):
    user_id = user["id"]
    
    # Analyze query to determine type
    query_analysis = query_analyzer.analyze_query(request.query)
    
    # Handle structured queries (count, filter, list)
    if query_analysis["type"] in ["count", "list"]:
        entity_type = query_analysis.get("entities", ["deals"])[0] if query_analysis.get("entities") else "deals"
        time_filter = query_analysis.get("time_filter")
        
        if query_analysis["type"] == "count":
            structured_result = structured_query_engine.execute_count_query(entity_type, user_id, time_filter)
            answer = f"Found {structured_result['count']} {entity_type}."
        else:
            structured_result = structured_query_engine.execute_list_query(entity_type, user_id, time_filter)
            answer = f"Here are {len(structured_result['items'])} {entity_type}:\n" + "\n".join([f"- {item.get('entity_text', 'Item')}" for item in structured_result['items'][:10]])
        
        return SearchResponse(
            answer=answer,
            results=[],
            kg_entities=structured_result.get('items', []),
            citations=[]
        )
    
    # Regular hybrid search for other queries
    search_results = search_engine.hybrid_search(request.query, user_id, request.top_k)
    kg_data = kg_builder.query_graph(request.query, user_id)
    
    # Generate answer (with fallback)
    try:
        answer_data = answer_generator.generate_answer(request.query, search_results)
    except Exception as e:
        print(f"Answer generation failed: {e}")
        answer_data = {
            "answer": f"Found {len(search_results)} results for your query.",
            "citations": []
        }
    
    results = [
        SearchResult(
            content=r["content"],
            score=r["score"],
            source=r["source"],
            metadata=r["metadata"]
        ) for r in search_results
    ]
    
    return SearchResponse(
        answer=answer_data["answer"],
        results=results,
        kg_entities=kg_data.get("nodes", []),
        kg_data=kg_data,
        citations=answer_data["citations"]
    )

@router.post("/feedback")
async def submit_feedback(request: FeedbackRequest, user: dict = Depends(get_current_user)):
    user_id = user["id"]
    
    # Store feedback for learning
    feedback_learner.store_feedback(
        query=request.query,
        answer=request.answer,
        rating=request.rating,
        user_id=user_id,
        comment=request.comment
    )
    
    return {"message": "Feedback received and stored for improvement", "rating": request.rating}

@router.get("/analytics")
async def get_search_analytics(user: dict = Depends(get_current_user)):
    patterns = feedback_learner.get_query_patterns()
    return patterns
