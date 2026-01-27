import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 6)
plt.rcParams['font.size'] = 10

# Load the dataset
data_path = "/home/ubuntu/.cache/kagglehub/datasets/karkavelrajaj/amazon-sales-dataset/versions/1/amazon.csv"
df = pd.read_csv(data_path)

print("=" * 80)
print("AMAZON SALES BUSINESS ANALYSIS")
print("=" * 80)

# Data Cleaning
print("\n1. DATA CLEANING")
print("-" * 80)

# Clean price columns (remove ₹ and commas)
df['discounted_price_clean'] = df['discounted_price'].str.replace('₹', '').str.replace(',', '').astype(float)
df['actual_price_clean'] = df['actual_price'].str.replace('₹', '').str.replace(',', '').astype(float)

# Clean discount percentage
df['discount_pct_clean'] = df['discount_percentage'].str.replace('%', '').astype(float)

# Clean rating (handle | separator)
df['rating_clean'] = df['rating'].str.split('|').str[0].str.strip()
df['rating_clean'] = pd.to_numeric(df['rating_clean'], errors='coerce')

# Clean rating count (remove commas)
df['rating_count_clean'] = df['rating_count'].str.replace(',', '').astype(float)

# Calculate revenue (discounted price * rating count as proxy for sales volume)
df['estimated_revenue'] = df['discounted_price_clean'] * df['rating_count_clean']

# Calculate savings
df['savings'] = df['actual_price_clean'] - df['discounted_price_clean']

print(f"✓ Cleaned price columns")
print(f"✓ Cleaned discount percentages")
print(f"✓ Cleaned ratings and counts")
print(f"✓ Calculated estimated revenue and savings")

# Extract main category (first part before |)
df['main_category'] = df['category'].str.split('|').str[0].str.strip()

print(f"✓ Extracted main categories: {df['main_category'].nunique()} unique categories")

# 2. KEY BUSINESS METRICS
print("\n2. KEY BUSINESS METRICS")
print("-" * 80)

total_products = len(df)
total_categories = df['main_category'].nunique()
avg_price = df['discounted_price_clean'].mean()
avg_discount = df['discount_pct_clean'].mean()
avg_rating = df['rating_clean'].mean()
total_reviews = df['rating_count_clean'].sum()
total_revenue = df['estimated_revenue'].sum()

print(f"Total Products: {total_products:,}")
print(f"Total Categories: {total_categories}")
print(f"Average Price: ₹{avg_price:,.2f}")
print(f"Average Discount: {avg_discount:.1f}%")
print(f"Average Rating: {avg_rating:.2f}/5.0")
print(f"Total Reviews: {total_reviews:,.0f}")
print(f"Estimated Total Revenue: ₹{total_revenue:,.0f}")

# 3. CATEGORY ANALYSIS
print("\n3. CATEGORY ANALYSIS")
print("-" * 80)

category_stats = df.groupby('main_category').agg({
    'product_id': 'count',
    'discounted_price_clean': 'mean',
    'discount_pct_clean': 'mean',
    'rating_clean': 'mean',
    'rating_count_clean': 'sum',
    'estimated_revenue': 'sum'
}).round(2)

category_stats.columns = ['Product Count', 'Avg Price', 'Avg Discount %', 'Avg Rating', 'Total Reviews', 'Est Revenue']
category_stats = category_stats.sort_values('Est Revenue', ascending=False)

print("\nTop 10 Categories by Revenue:")
print(category_stats.head(10))

# 4. PRICING ANALYSIS
print("\n4. PRICING ANALYSIS")
print("-" * 80)

price_segments = pd.cut(df['discounted_price_clean'], 
                        bins=[0, 500, 1000, 2000, 5000, float('inf')],
                        labels=['Budget (<₹500)', 'Economy (₹500-1K)', 'Mid-range (₹1K-2K)', 
                               'Premium (₹2K-5K)', 'Luxury (>₹5K)'])
df['price_segment'] = price_segments

price_analysis = df.groupby('price_segment').agg({
    'product_id': 'count',
    'rating_clean': 'mean',
    'discount_pct_clean': 'mean',
    'estimated_revenue': 'sum'
}).round(2)

price_analysis.columns = ['Product Count', 'Avg Rating', 'Avg Discount %', 'Est Revenue']
print(price_analysis)

# 5. DISCOUNT ANALYSIS
print("\n5. DISCOUNT ANALYSIS")
print("-" * 80)

discount_segments = pd.cut(df['discount_pct_clean'],
                           bins=[0, 20, 40, 60, 80, 100],
                           labels=['Low (0-20%)', 'Medium (20-40%)', 'High (40-60%)', 
                                  'Very High (60-80%)', 'Extreme (80-100%)'])
df['discount_segment'] = discount_segments

discount_analysis = df.groupby('discount_segment').agg({
    'product_id': 'count',
    'rating_clean': 'mean',
    'rating_count_clean': 'mean',
    'estimated_revenue': 'sum'
}).round(2)

discount_analysis.columns = ['Product Count', 'Avg Rating', 'Avg Review Count', 'Est Revenue']
print(discount_analysis)

# 6. RATING ANALYSIS
print("\n6. RATING ANALYSIS")
print("-" * 80)

rating_dist = df['rating_clean'].value_counts().sort_index(ascending=False)
print("\nRating Distribution:")
print(rating_dist.head(10))

high_rated = len(df[df['rating_clean'] >= 4.0])
low_rated = len(df[df['rating_clean'] < 3.0])

print(f"\nHigh-rated products (≥4.0): {high_rated} ({high_rated/len(df)*100:.1f}%)")
print(f"Low-rated products (<3.0): {low_rated} ({low_rated/len(df)*100:.1f}%)")

# 7. TOP PERFORMERS
print("\n7. TOP PERFORMING PRODUCTS")
print("-" * 80)

top_revenue = df.nlargest(10, 'estimated_revenue')[['product_name', 'main_category', 
                                                      'discounted_price_clean', 'rating_clean', 
                                                      'rating_count_clean', 'estimated_revenue']]
print("\nTop 10 by Estimated Revenue:")
print(top_revenue.to_string(index=False))

top_rated = df[df['rating_count_clean'] >= 100].nlargest(10, 'rating_clean')[
    ['product_name', 'main_category', 'rating_clean', 'rating_count_clean']]
print("\nTop 10 Highest Rated (min 100 reviews):")
print(top_rated.to_string(index=False))

# Save cleaned data
output_path = '/home/ubuntu/amazon_cleaned_data.csv'
df.to_csv(output_path, index=False)
print(f"\n✓ Cleaned data saved to: {output_path}")

# Save analysis summary
with open('/home/ubuntu/analysis_summary.txt', 'w') as f:
    f.write("AMAZON SALES BUSINESS ANALYSIS SUMMARY\n")
    f.write("=" * 80 + "\n\n")
    f.write("KEY METRICS\n")
    f.write("-" * 80 + "\n")
    f.write(f"Total Products: {total_products:,}\n")
    f.write(f"Total Categories: {total_categories}\n")
    f.write(f"Average Price: ₹{avg_price:,.2f}\n")
    f.write(f"Average Discount: {avg_discount:.1f}%\n")
    f.write(f"Average Rating: {avg_rating:.2f}/5.0\n")
    f.write(f"Total Reviews: {total_reviews:,.0f}\n")
    f.write(f"Estimated Total Revenue: ₹{total_revenue:,.0f}\n\n")
    
    f.write("TOP 5 CATEGORIES BY REVENUE\n")
    f.write("-" * 80 + "\n")
    f.write(category_stats.head(5).to_string())
    f.write("\n\n")
    
    f.write("PRICE SEGMENT ANALYSIS\n")
    f.write("-" * 80 + "\n")
    f.write(price_analysis.to_string())

print("\n✓ Analysis summary saved to: analysis_summary.txt")

print("\n" + "=" * 80)
print("BUSINESS ANALYSIS COMPLETE!")
print("=" * 80)
