import streamlit as st
from query_flow import pipelines

st.title("QueryFlow - Explainable Retrieval")

st.markdown("### Try examples:")

col1, col2, col3 = st.columns(3)
with col1:
    if st.button("Names starting with A"):
        st.session_state.example_query = "Find people whose first name starts with A"
with col2:
    if st.button("20th century constraint"):
        st.session_state.example_query = "Find people active in the 20th century but born before 1900"
with col3:
    if st.button("Not born in Europe"):
        st.session_state.example_query = "Find people not born in Europe"

query = st.text_input("Enter your query", value=st.session_state.get("example_query", ""))

pipeline_type = st.selectbox(
    "Pipeline",
    ["statistical", "hybrid", "rag"]
)

debug = st.checkbox("Debug mode", value=True)

def format_score(value):
    if value >= 0.7:
        return "High"
    if value >= 0.3:
        return "Medium"
    if value > 0:
        return "Low"
    return "None"


def get_main_reason(exp, qtype=None):
    if not exp:
        return "N/A"
    if exp.get("rule", 0) > 0:
        return "Rule-based filtering"
    if exp.get("metadata", 0) > 0:
        return "Metadata condition"
    if exp.get("dense", 0) > exp.get("bm25", 0):
        return "Semantic similarity"
    if exp.get("bm25", 0) > 0:
        return "Keyword match"
    return "No match"


def get_tie_breaker(exp):
    dense = exp.get("dense", 0)
    bm25 = exp.get("bm25", 0)
    rule = exp.get("rule", 0)
    metadata = exp.get("metadata", 0)

    if dense <= 0:
        return ""

    if dense < 0.15:
        return "Tie-breaker: Not significant"

    if rule > 0 or metadata > 0 or bm25 > 0:
        return "Tie-breaker: Semantic similarity"

    return "Tie-breaker: Keyword match"


def get_system_behaviour(results):
    if not results:
        return ""

    has_dense = False
    has_bm25 = False
    has_rule = False
    has_metadata = False

    for r in results:
        exp = r.get("explanation", {}) or r.get("score_breakdown", {})
        has_dense = has_dense or exp.get("dense", 0) > 0
        has_bm25 = has_bm25 or exp.get("bm25", 0) > 0
        has_rule = has_rule or exp.get("rule", 0) > 0
        has_metadata = has_metadata or exp.get("metadata", 0) > 0

    if not has_rule and not has_metadata:
        if has_dense and has_bm25:
            return "Semantic + keyword ranking (no constraints matched)"
        if has_dense:
            return "Semantic ranking (no constraints matched)"
        if has_bm25:
            return "Keyword ranking (no constraints matched)"
        return "No active signals"

    parts = []
    if has_dense:
        parts.append("semantic")
    if has_bm25:
        parts.append("keyword")
    if has_rule:
        parts.append("rule scoring")
    if has_metadata:
        parts.append("metadata scoring")

    return " + ".join(parts)


if st.button("Run") and query:
    flow = getattr(pipelines, pipeline_type)()
    try:
        result = flow.run(query, debug=debug)
    except ImportError as exc:
        st.error(str(exc))
        st.stop()

    st.subheader("Results")

    show_breakdown = st.checkbox("Show score breakdown visually", value=False)

    results = result.results
    trace = result.trace or []
    debug_info = result.debug_info or {}

    qa = debug_info.get("query_analysis", {})
    qtype = qa.get("detected_type", "unknown")

    for i, r in enumerate(results, 1):
        exp = r.get("explanation", {}) or r.get("score_breakdown", {})
        main_reason = get_main_reason(exp, qtype)
        tie_breaker = get_tie_breaker(exp)
        
        st.markdown(f"**{i}. {r.get('doc_id', 'N/A')}** - Score: {r.get('score', 0):.3f}")
        st.markdown(f"**Main reason:** {main_reason}")
        if tie_breaker:
            st.markdown(f"_{tie_breaker}_")
        st.write(r.get("text", "")[:200] + "...")

        if debug and exp:
            with st.expander("Explanation"):
                if exp.get("rule", 0) > 0:
                    st.write(f"**Primary signal:** Rule-based filtering")
                    st.write(f"**Secondary signal:** Semantic similarity")
                elif exp.get("metadata", 0) > 0:
                    st.write(f"**Primary signal:** Metadata condition")
                    st.write(f"**Secondary signal:** Semantic similarity")
                elif exp.get("dense", 0) >= 0.7:
                    st.write(f"**Primary signal:** Semantic similarity")
                elif exp.get("bm25", 0) > exp.get("dense", 0):
                    st.write(f"**Primary signal:** Keyword match")
                else:
                    st.write(f"**Primary signal:** Semantic similarity")
                
                st.write(f"**Signals:**")
                st.write(f"- Semantic similarity: {exp.get('dense', 0):.3f}")
                st.write(f"- Keyword relevance: {exp.get('bm25', 0):.3f}")
                st.write(f"- Rule applied: {'Yes' if exp.get('rule', 0) > 0 else 'No'}")
                st.write(f"- Metadata condition: {'Yes' if exp.get('metadata', 0) > 0 else 'No'}")

                if show_breakdown:
                    st.bar_chart({
                        "Semantic": exp.get("dense", 0),
                        "Keyword": exp.get("bm25", 0),
                        "Rule": exp.get("rule", 0),
                        "Metadata": exp.get("metadata", 0)
                    })

    if debug:
        qa = debug_info.get("query_analysis", {})
        qtype = qa.get("detected_type", "unknown")
        rewritten = qa.get("rewritten_query", query)
        
        st.subheader("Query Understanding")
        st.write(f"**Interpreted as:** {qtype}")
        
        if rewritten and rewritten != query:
            st.write(f"**Rewritten to:** {rewritten}")
        
        system_behaviour = get_system_behaviour(results) or qa.get("suggested_retrieval", "")
        if system_behaviour:
            st.write(f"**System behaviour:** {system_behaviour}")

        st.subheader("Pipeline Trace")
        for step in trace:
            st.write(f"→ {step.get('step')} ({step.get('node_type')})")
