import streamlit as st
import pandas as pd
import textwrap

def render_model_page():
    st.markdown("### 📊 Model UI – Performance Analysis & Evaluation")
    st.markdown("""
    This section presents the canonical evaluation metrics. 
    The models were trained purely on historical data up to **2024-06-30** and validated 
    via strict walk-forward evaluation from **2024-07-01** onwards.
    
    Evaluators can assess model performance and compute **Mean Absolute Error (MAE)** against actual Dream Teams.
    
    $$\\text{MAE} = \\left| \\text{Total Dream Team Fantasy Points} - \\text{Total Fantasy Points of Predicted Team} \\right|$$
    """)
    
    st.markdown("---")
    st.markdown("#### 🚀 M7 Final Evaluation Metrics")
    st.markdown("These are the exact holdout evaluation metrics from the `reports/m7_final_summary.csv` artifact.")
    
    try:
        m7_df = pd.read_csv('reports/m7_final_summary.csv')
        metrics = m7_df.iloc[0].to_dict()
        
        c1, c2, c3, c4 = st.columns(4)
        c1_m = textwrap.dedent(f'<div class="kpi-card"><div class="kpi-val">{metrics.get("Holdout Matches", 244)}</div><div class="kpi-lbl">Holdout Matches</div></div>')
        c2_m = textwrap.dedent(f'<div class="kpi-card"><div class="kpi-val" style="color:#10b981;">{metrics.get("Mean Recall@11", 0.7168):.4f}</div><div class="kpi-lbl">Recall@11</div></div>')
        c3_m = textwrap.dedent(f'<div class="kpi-card"><div class="kpi-val">{metrics.get("Mean XI Overlap", 7.8852):.2f} / 11</div><div class="kpi-lbl">Mean Squad Overlap</div></div>')
        c4_m = textwrap.dedent(f'<div class="kpi-card"><div class="kpi-val" style="color:#FF3B44;">{metrics.get("Mean Team Regret", 296.3):.1f}</div><div class="kpi-lbl">Mean Team Regret</div></div>')
        
        c1.markdown(c1_m, unsafe_allow_html=True)
        c2.markdown(c2_m, unsafe_allow_html=True)
        c3.markdown(c3_m, unsafe_allow_html=True)
        c4.markdown(c4_m, unsafe_allow_html=True)
        
        st.write(f"**Captain Accuracy (in-play):** {metrics.get('Captain Acc (in-play)', 0.791)*100:.1f}%")
        st.write(f"**Training window:** {metrics.get('Training Window', '2015-01-01 to 2024-06-30')}")
        st.write(f"**Leakage Status:** {metrics.get('Leakage Status', 'CLEAN')}")
        
    except Exception as e:
        st.error(f"Could not load M7 metrics: {str(e)}")
        
    st.markdown("---")
    st.markdown("#### 🧠 Global Model Insights (SHAP)")
    st.markdown("Global feature importance based on mean absolute SHAP values across the holdout set.")
    
    try:
        with open('reports/m8_shap_report.md', 'r') as f:
            shap_report = f.read()
        st.markdown(shap_report)
    except Exception as e:
        st.info("M8 report not found. Run m8_shap_evaluation.py first to generate SHAP report.")

    st.markdown("---")
    st.markdown("#### 🏗️ Architecture Pipeline")
    st.code("""
    [ Historical Data strictly < D ]
             |
    [ Pre-toss Candidate Pool ]
             |
    [ Feature Engineering ]
             |
    [ FP Model ]   [ P(play) Model ]
             \\       /
        [ Expected FP ]
             |
       [ ILP Optimizer ]
             |
     [ Best XI + C/VC ]
             |
    [ SHAP Explainability ]
    """, language="text")
