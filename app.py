import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from analysis import CORD19Analyzer, create_visualizations
import plotly.express as px
import plotly.graph_objects as go
from wordcloud import WordCloud
import io

# Page configuration
st.set_page_config(
    page_title="CORD-19 Data Explorer",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .section-header {
        font-size: 1.5rem;
        color: #2e86ab;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

def main():
    # Header
    st.markdown('<div class="main-header">🔬 CORD-19 COVID-19 Research Data Explorer</div>', 
                unsafe_allow_html=True)
    
    st.write("""
    This interactive application explores the CORD-19 dataset containing metadata 
    about COVID-19 research papers. Use the sidebar to filter data and explore insights.
    """)
    
    # Initialize analyzer
    if 'analyzer' not in st.session_state:
        st.session_state.analyzer = CORD19Analyzer('data/metadata.csv')
        
        # Load and clean data
        with st.spinner('Loading data... This may take a moment for large datasets.'):
            if st.session_state.analyzer.load_data():
                st.session_state.analyzer.clean_data()
                st.success('Data loaded and cleaned successfully!')
            else:
                st.error('Error loading data. Please check if metadata.csv is in the data folder.')
                return
    
    analyzer = st.session_state.analyzer
    df_clean = analyzer.df_clean
    
    # Sidebar
    st.sidebar.title("Filters and Controls")
    
    # Year range selector
    st.sidebar.markdown("### Publication Year Range")
    min_year = int(df_clean['publication_year'].min()) if not df_clean['publication_year'].isna().all() else 2019
    max_year = int(df_clean['publication_year'].max()) if not df_clean['publication_year'].isna().all() else 2023
    
    year_range = st.sidebar.slider(
        "Select year range:",
        min_value=min_year,
        max_value=max_year,
        value=(min_year, max_year)
    )
    
    # Journal filter
    st.sidebar.markdown("### Journal Filter")
    top_journals = analyzer.analyze_top_journals(20)
    selected_journals = st.sidebar.multiselect(
        "Select journals to include:",
        options=top_journals.index.tolist(),
        default=top_journals.index.tolist()[:5]
    )
    
    # Source filter
    st.sidebar.markdown("### Source Filter")
    sources = df_clean['source_x'].dropna().unique().tolist()
    selected_sources = st.sidebar.multiselect(
        "Select sources to include:",
        options=sources,
        default=sources[:3] if len(sources) > 3 else sources
    )
    
    # Apply filters
    filtered_df = df_clean.copy()
    
    # Filter by year
    filtered_df = filtered_df[
        (filtered_df['publication_year'] >= year_range[0]) & 
        (filtered_df['publication_year'] <= year_range[1])
    ]
    
    # Filter by journal
    if selected_journals:
        filtered_df = filtered_df[filtered_df['journal_clean'].isin(selected_journals)]
    
    # Filter by source
    if selected_sources:
        filtered_df = filtered_df[filtered_df['source_x'].isin(selected_sources)]
    
    # Main content tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Overview", 
        "📈 Trends", 
        "🔍 Word Analysis", 
        "📋 Data Sample"
    ])
    
    with tab1:
        st.markdown('<div class="section-header">Dataset Overview</div>', 
                    unsafe_allow_html=True)
        
        # Key metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Papers", f"{len(filtered_df):,}")
        
        with col2:
            st.metric("Unique Journals", f"{filtered_df['journal_clean'].nunique():,}")
        
        with col3:
            avg_words = filtered_df['abstract_word_count'].mean()
            st.metric("Avg Abstract Words", f"{avg_words:.0f}")
        
        with col4:
            complete_abstracts = filtered_df[filtered_df['abstract_word_count'] > 0].shape[0]
            st.metric("Papers with Abstracts", f"{complete_abstracts:,}")
        
        # Publications by year (interactive)
        st.markdown('<div class="section-header">Publications Over Time</div>', 
                    unsafe_allow_html=True)
        
        yearly_counts = filtered_df['publication_year'].value_counts().sort_index()
        fig_time = px.line(
            x=yearly_counts.index, 
            y=yearly_counts.values,
            labels={'x': 'Year', 'y': 'Number of Publications'},
            title='Publication Trends Over Time'
        )
        st.plotly_chart(fig_time, use_container_width=True)
    
    with tab2:
        st.markdown('<div class="section-header">Publication Trends Analysis</div>', 
                    unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Top journals chart
            top_journals_filtered = filtered_df['journal_clean'].value_counts().head(10)
            fig_journals = px.bar(
                x=top_journals_filtered.values,
                y=top_journals_filtered.index,
                orientation='h',
                labels={'x': 'Number of Publications', 'y': 'Journal'},
                title='Top 10 Journals by Publication Count'
            )
            st.plotly_chart(fig_journals, use_container_width=True)
        
        with col2:
            # Source distribution
            source_dist = filtered_df['source_x'].value_counts().head(10)
            fig_source = px.pie(
                values=source_dist.values,
                names=source_dist.index,
                title='Paper Distribution by Source'
            )
            st.plotly_chart(fig_source, use_container_width=True)
        
        # Monthly trends
        st.markdown('<div class="section-header">Monthly Publication Trends</div>', 
                    unsafe_allow_html=True)
        
        monthly_data = filtered_df.copy()
        monthly_data['publish_month'] = monthly_data['publish_time'].dt.to_period('M')
        monthly_counts = monthly_data['publish_month'].value_counts().sort_index()
        
        if len(monthly_counts) > 0:
            monthly_counts.index = monthly_counts.index.astype(str)
            fig_monthly = px.line(
                x=monthly_counts.index,
                y=monthly_counts.values,
                labels={'x': 'Month', 'y': 'Publications'},
                title='Monthly Publication Count'
            )
            fig_monthly.update_xaxes(tickangle=45)
            st.plotly_chart(fig_monthly, use_container_width=True)
    
    with tab3:
        st.markdown('<div class="section-header">Text Analysis</div>', 
                    unsafe_allow_html=True)
        
        # Word cloud
        st.subheader("Word Cloud of Paper Titles")
        
        # Create word cloud
        text_data = ' '.join(filtered_df['title'].dropna().astype(str))
        if text_data.strip():
            wordcloud = WordCloud(width=800, height=400, background_color='white').generate(text_data)
            
            fig, ax = plt.subplots(figsize=(10, 5))
            ax.imshow(wordcloud, interpolation='bilinear')
            ax.axis('off')
            st.pyplot(fig)
        else:
            st.warning("No text data available for word cloud generation.")
        
        # Word frequencies
        st.subheader("Most Frequent Words")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Title words
            title_words = analyzer.analyze_word_frequencies('title', 15)
            if title_words:
                fig_title_words = px.bar(
                    x=list(title_words.values()),
                    y=list(title_words.keys()),
                    orientation='h',
                    labels={'x': 'Frequency', 'y': 'Words'},
                    title='Top 15 Words in Titles'
                )
                st.plotly_chart(fig_title_words, use_container_width=True)
        
        with col2:
            # Abstract words (if available)
            abstract_text = ' '.join(filtered_df['abstract'].dropna().astype(str))
            if len(abstract_text) > 100:  # Only show if we have substantial abstract data
                abstract_words = analyzer.analyze_word_frequencies('abstract', 15)
                if abstract_words:
                    fig_abstract_words = px.bar(
                        x=list(abstract_words.values()),
                        y=list(abstract_words.keys()),
                        orientation='h',
                        labels={'x': 'Frequency', 'y': 'Words'},
                        title='Top 15 Words in Abstracts'
                    )
                    st.plotly_chart(fig_abstract_words, use_container_width=True)
    
    with tab4:
        st.markdown('<div class="section-header">Data Sample</div>', 
                    unsafe_allow_html=True)
        
        st.write(f"Showing sample of {len(filtered_df):,} filtered papers")
        
        # Data sample with selected columns
        display_columns = ['title', 'journal_clean', 'publication_year', 'source_x', 'abstract_word_count']
        available_columns = [col for col in display_columns if col in filtered_df.columns]
        
        st.dataframe(
            filtered_df[available_columns].head(100),
            use_container_width=True,
            height=400
        )
        
        # Data summary
        st.subheader("Data Summary")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Column Information:**")
            col_info = pd.DataFrame({
                'Column': filtered_df.columns,
                'Non-Null Count': filtered_df.notnull().sum(),
                'Data Type': filtered_df.dtypes
            })
            st.dataframe(col_info, use_container_width=True)
        
        with col2:
            st.write("**Missing Values Summary:**")
            missing_data = filtered_df.isnull().sum()
            missing_percent = (missing_data / len(filtered_df)) * 100
            missing_df = pd.DataFrame({
                'Missing Count': missing_data,
                'Missing Percentage': missing_percent
            }).sort_values('Missing Count', ascending=False)
            st.dataframe(missing_df.head(10), use_container_width=True)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    **CORD-19 Data Explorer** | Created for Frameworks Assignment  
    *Dataset: COVID-19 Open Research Dataset (CORD-19) from Allen Institute for AI*
    """)

if __name__ == "__main__":
    main()