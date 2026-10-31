import streamlit as st
from agent import run_osint_agent, resolve_domain

st.set_page_config(page_title="Nexus OSINT Intelligence", layout="wide")

st.markdown("## Nexus Entity Intelligence")
st.markdown(
    "Autonomous institutional due diligence and synthetic risk detection.")
st.markdown("---")

col1, col2 = st.columns([4, 1])
with col1:
    # Changed to accept natural language!
    query_input = st.text_input(
        "Target Entity", placeholder="Enter any company name (e.g., 'OpenAI', 'Zomato food delivery')", label_visibility="collapsed")
with col2:
    run_btn = st.button("Execute Analysis", type="primary",
                        use_container_width=True)

if run_btn and query_input:
    # STEP 1: The NLP Routing Agent
    with st.spinner("Agent mapping natural language to institutional domain..."):
        resolved_domain = resolve_domain(query_input)

    if not resolved_domain:
        st.error("SYSTEM FAULT: Could not resolve a valid domain for that input.")
    else:
        st.info(f"Target Resolved: `{resolved_domain}`")

        # STEP 2: The Data & Intelligence Agent
        with st.spinner(f"Aggregating institutional data for {resolved_domain}..."):
            result = run_osint_agent(resolved_domain)

            if result.get("error"):
                st.error(f"SYSTEM FAULT: {result['message']}")
            else:
                data = result["footprint_data"]

                st.markdown(f"### Target: `{data['company_name']}`")

                m1, m2, m3, m4 = st.columns(4)
                m1.metric("Risk Index", f"{data['risk_score_out_of_100']}/100")
                m2.metric("Verified Headcount", f"{data['headcount']:,}")
                m3.metric("Total Capital", f"${data['funding']:,.0f}")
                m4.metric("Capital per Head",
                          f"${data['capital_per_employee']:,.0f}")

                st.markdown("<br>", unsafe_allow_html=True)

                if data["risk_score_out_of_100"] > 50:
                    st.error("STATUS: HIGH-RISK PROFILE DETECTED")
                else:
                    st.success("STATUS: OPERATIONAL ENTITY VERIFIED")

                if data["algorithmic_flags"]:
                    st.markdown("**System Anomalies Detected:**")
                    for flag in data["algorithmic_flags"]:
                        st.markdown(f"- {flag}")

                st.markdown("---")

                st.markdown("### Intelligence Briefing")
                st.markdown(result["agent_briefing"])
