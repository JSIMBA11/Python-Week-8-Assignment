import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud
from collections import Counter
import re
from datetime import datetime

class CORD19Analyzer:
    def __init__(self, file_path='data/metadata.csv'):
        """
        Initialize the CORD-19 data analyzer
        
        Args:
            file_path (str): Path to the metadata.csv file
        """
        self.file_path = file_path
        self.df = None
        self.df_clean = None
        
    def load_data(self):
        """
        Load the CORD-19 metadata file
        """
        try:
            self.df = pd.read_csv(self.file_path)
            print(f"Data loaded successfully: {self.df.shape[0]} rows, {self.df.shape[1]} columns")
            return True
        except Exception as e:
            print(f"Error loading data: {e}")
            return False
    
    def explore_data(self):
        """
        Perform basic data exploration
        """
        if self.df is None:
            print("Please load data first")
            return None
        
        exploration_results = {
            'shape': self.df.shape,
            'columns': self.df.columns.tolist(),
            'dtypes': self.df.dtypes,
            'missing_values': self.df.isnull().sum(),
            'basic_stats': self.df.describe(include='all')
        }
        
        return exploration_results
    
    def clean_data(self):
        """
        Clean and prepare the data for analysis
        """
        if self.df is None:
            print("Please load data first")
            return None
        
        # Create a copy for cleaning
        self.df_clean = self.df.copy()
        
        # Handle missing values
        # Keep papers that have at least title or abstract
        self.df_clean = self.df_clean.dropna(subset=['title'], how='all')
        
        # Fill missing abstracts with empty string
        self.df_clean['abstract'] = self.df_clean['abstract'].fillna('')
        
        # Convert publish_time to datetime
        self.df_clean['publish_time'] = pd.to_datetime(
            self.df_clean['publish_time'], errors='coerce'
        )
        
        # Extract year from publication date
        self.df_clean['publication_year'] = self.df_clean['publish_time'].dt.year
        
        # Create abstract word count
        self.df_clean['abstract_word_count'] = self.df_clean['abstract'].apply(
            lambda x: len(str(x).split())
        )
        
        # Clean journal names
        self.df_clean['journal_clean'] = self.df_clean['journal'].fillna('Unknown')
        self.df_clean['journal_clean'] = self.df_clean['journal_clean'].str.strip().str.title()
        
        print(f"Data cleaned: {self.df_clean.shape[0]} rows remaining")
        return self.df_clean
    
    def analyze_publications_over_time(self):
        """
        Analyze publication trends over time
        """
        if self.df_clean is None:
            print("Please clean data first")
            return None
        
        # Remove papers with invalid years
        valid_years = self.df_clean.dropna(subset=['publication_year'])
        valid_years = valid_years[valid_years['publication_year'] >= 2019]
        valid_years = valid_years[valid_years['publication_year'] <= 2023]
        
        publications_by_year = valid_years['publication_year'].value_counts().sort_index()
        
        return publications_by_year
    
    def analyze_top_journals(self, top_n=10):
        """
        Identify top journals publishing COVID-19 research
        """
        if self.df_clean is None:
            print("Please clean data first")
            return None
        
        top_journals = self.df_clean['journal_clean'].value_counts().head(top_n)
        return top_journals
    
    def analyze_word_frequencies(self, column='title', top_n=20):
        """
        Analyze most frequent words in titles or abstracts
        """
        if self.df_clean is None:
            print("Please clean data first")
            return None
        
        # Combine all text
        all_text = ' '.join(self.df_clean[column].dropna().astype(str))
        
        # Clean text: remove punctuation, numbers, and convert to lowercase
        words = re.findall(r'\b[a-zA-Z]{3,}\b', all_text.lower())
        
        # Remove common stop words
        stop_words = {'the', 'and', 'of', 'in', 'to', 'a', 'for', 'with', 'on', 'by', 
                     'as', 'an', 'from', 'that', 'this', 'is', 'are', 'was', 'were', 
                     'be', 'has', 'have', 'had', 'but', 'not', 'at', 'which', 'or', 
                     'it', 'its', 'their', 'they', 'them', 'these', 'those', 'such'}
        
        filtered_words = [word for word in words if word not in stop_words]
        
        # Get word frequencies
        word_freq = Counter(filtered_words)
        top_words = dict(word_freq.most_common(top_n))
        
        return top_words
    
    def create_wordcloud(self, column='title'):
        """
        Generate a word cloud from titles or abstracts
        """
        if self.df_clean is None:
            print("Please clean data first")
            return None
        
        text = ' '.join(self.df_clean[column].dropna().astype(str))
        
        wordcloud = WordCloud(
            width=800, 
            height=400, 
            background_color='white',
            max_words=100
        ).generate(text)
        
        return wordcloud
    
    def analyze_sources(self):
        """
        Analyze paper distribution by source
        """
        if self.df_clean is None:
            print("Please clean data first")
            return None
        
        source_distribution = self.df_clean['source_x'].value_counts().head(10)
        return source_distribution

def create_visualizations(analyzer):
    """
    Create all required visualizations
    """
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    
    # 1. Publications over time
    publications_by_year = analyzer.analyze_publications_over_time()
    axes[0, 0].bar(publications_by_year.index, publications_by_year.values)
    axes[0, 0].set_title('COVID-19 Publications by Year')
    axes[0, 0].set_xlabel('Year')
    axes[0, 0].set_ylabel('Number of Publications')
    axes[0, 0].tick_params(axis='x', rotation=45)
    
    # 2. Top journals
    top_journals = analyzer.analyze_top_journals(10)
    axes[0, 1].barh(range(len(top_journals)), top_journals.values)
    axes[0, 1].set_yticks(range(len(top_journals)))
    axes[0, 1].set_yticklabels(top_journals.index)
    axes[0, 1].set_title('Top 10 Journals Publishing COVID-19 Research')
    axes[0, 1].set_xlabel('Number of Publications')
    
    # 3. Word frequencies
    word_freq = analyzer.analyze_word_frequencies('title', 15)
    axes[1, 0].bar(range(len(word_freq)), list(word_freq.values()))
    axes[1, 0].set_xticks(range(len(word_freq)))
    axes[1, 0].set_xticklabels(list(word_freq.keys()), rotation=45, ha='right')
    axes[1, 0].set_title('Most Frequent Words in Paper Titles')
    axes[1, 0].set_ylabel('Frequency')
    
    # 4. Source distribution
    source_dist = analyzer.analyze_sources()
    axes[1, 1].pie(source_dist.values, labels=source_dist.index, autopct='%1.1f%%')
    axes[1, 1].set_title('Paper Distribution by Source')
    
    plt.tight_layout()
    return fig