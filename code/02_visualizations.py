import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.dpi'] = 100
plt.rcParams['savefig.dpi'] = 150
plt.rcParams['font.size'] = 10

# Load cleaned data
df = pd.read_csv('/home/ubuntu/amazon_cleaned_data.csv')

# Create output directory
import os
os.makedirs('/home/ubuntu/amazon_viz', exist_ok=True)

print("Creating visualizations...")

# 1. Category Revenue Distribution
print("1. Category revenue distribution...")
fig, ax = plt.subplots(figsize=(14, 8))
top_categories = df.groupby('main_category')['estimated_revenue'].sum().nlargest(15).sort_values()
top_categories.plot(kind='barh', ax=ax, color='steelblue')
ax.set_xlabel('Estimated Revenue (₹)', fontsize=12, fontweight='bold')
ax.set_ylabel('Category', fontsize=12, fontweight='bold')
ax.set_title('Top 15 Categories by Estimated Revenue', fontsize=14, fontweight='bold', pad=20)
ax.grid(axis='x', alpha=0.3)
for i, v in enumerate(top_categories.values):
    ax.text(v, i, f' ₹{v/1e9:.2f}B', va='center', fontsize=9)
plt.tight_layout()
plt.savefig('/home/ubuntu/amazon_viz/01_category_revenue.png', bbox_inches='tight')
plt.close()

# 2. Price Distribution
print("2. Price distribution...")
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

# Histogram
ax1.hist(df['discounted_price_clean'], bins=50, color='coral', edgecolor='black', alpha=0.7)
ax1.set_xlabel('Discounted Price (₹)', fontsize=11, fontweight='bold')
ax1.set_ylabel('Frequency', fontsize=11, fontweight='bold')
ax1.set_title('Price Distribution', fontsize=12, fontweight='bold')
ax1.axvline(df['discounted_price_clean'].median(), color='red', linestyle='--', linewidth=2, label=f'Median: ₹{df["discounted_price_clean"].median():.0f}')
ax1.legend()
ax1.grid(alpha=0.3)

# Box plot by price segment
price_order = ['Budget (<₹500)', 'Economy (₹500-1K)', 'Mid-range (₹1K-2K)', 'Premium (₹2K-5K)', 'Luxury (>₹5K)']
df_price = df[df['price_segment'].notna()]
sns.boxplot(data=df_price, y='price_segment', x='rating_clean', order=price_order, ax=ax2, palette='Set2')
ax2.set_xlabel('Rating', fontsize=11, fontweight='bold')
ax2.set_ylabel('Price Segment', fontsize=11, fontweight='bold')
ax2.set_title('Rating by Price Segment', fontsize=12, fontweight='bold')
ax2.grid(axis='x', alpha=0.3)

plt.tight_layout()
plt.savefig('/home/ubuntu/amazon_viz/02_price_analysis.png', bbox_inches='tight')
plt.close()

# 3. Discount Analysis
print("3. Discount analysis...")
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

# Discount distribution
ax1.hist(df['discount_pct_clean'], bins=30, color='lightgreen', edgecolor='black', alpha=0.7)
ax1.set_xlabel('Discount Percentage (%)', fontsize=11, fontweight='bold')
ax1.set_ylabel('Frequency', fontsize=11, fontweight='bold')
ax1.set_title('Discount Distribution', fontsize=12, fontweight='bold')
ax1.axvline(df['discount_pct_clean'].median(), color='red', linestyle='--', linewidth=2, label=f'Median: {df["discount_pct_clean"].median():.0f}%')
ax1.legend()
ax1.grid(alpha=0.3)

# Revenue by discount segment
discount_order = ['Low (0-20%)', 'Medium (20-40%)', 'High (40-60%)', 'Very High (60-80%)', 'Extreme (80-100%)']
df_discount = df[df['discount_segment'].notna()]
discount_revenue = df_discount.groupby('discount_segment')['estimated_revenue'].sum().reindex(discount_order) / 1e9
discount_revenue.plot(kind='bar', ax=ax2, color='teal', edgecolor='black')
ax2.set_xlabel('Discount Segment', fontsize=11, fontweight='bold')
ax2.set_ylabel('Estimated Revenue (₹ Billions)', fontsize=11, fontweight='bold')
ax2.set_title('Revenue by Discount Segment', fontsize=12, fontweight='bold')
ax2.set_xticklabels(ax2.get_xticklabels(), rotation=45, ha='right')
ax2.grid(axis='y', alpha=0.3)
for i, v in enumerate(discount_revenue.values):
    ax2.text(i, v, f'₹{v:.2f}B', ha='center', va='bottom', fontsize=9, fontweight='bold')

plt.tight_layout()
plt.savefig('/home/ubuntu/amazon_viz/03_discount_analysis.png', bbox_inches='tight')
plt.close()

# 4. Rating Analysis
print("4. Rating analysis...")
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

# Rating distribution
rating_counts = df['rating_clean'].value_counts().sort_index()
ax1.bar(rating_counts.index, rating_counts.values, color='skyblue', edgecolor='black', alpha=0.8)
ax1.set_xlabel('Rating', fontsize=11, fontweight='bold')
ax1.set_ylabel('Number of Products', fontsize=11, fontweight='bold')
ax1.set_title('Product Rating Distribution', fontsize=12, fontweight='bold')
ax1.grid(axis='y', alpha=0.3)

# Scatter: Rating vs Review Count
sample_df = df.sample(min(500, len(df)))
ax2.scatter(sample_df['rating_clean'], sample_df['rating_count_clean'], 
           alpha=0.5, s=50, c=sample_df['discount_pct_clean'], cmap='viridis', edgecolors='black', linewidth=0.5)
ax2.set_xlabel('Rating', fontsize=11, fontweight='bold')
ax2.set_ylabel('Review Count', fontsize=11, fontweight='bold')
ax2.set_title('Rating vs Review Count (colored by discount %)', fontsize=12, fontweight='bold')
ax2.set_yscale('log')
ax2.grid(alpha=0.3)
cbar = plt.colorbar(ax2.collections[0], ax=ax2)
cbar.set_label('Discount %', fontsize=10)

plt.tight_layout()
plt.savefig('/home/ubuntu/amazon_viz/04_rating_analysis.png', bbox_inches='tight')
plt.close()

# 5. Top Products Dashboard
print("5. Top products dashboard...")
fig = plt.figure(figsize=(16, 10))
gs = fig.add_gridspec(3, 2, hspace=0.3, wspace=0.3)

# Top 10 products by revenue
ax1 = fig.add_subplot(gs[0, :])
top_10_revenue = df.nlargest(10, 'estimated_revenue')
y_pos = np.arange(len(top_10_revenue))
ax1.barh(y_pos, top_10_revenue['estimated_revenue'] / 1e9, color='gold', edgecolor='black')
ax1.set_yticks(y_pos)
ax1.set_yticklabels([name[:50] + '...' if len(name) > 50 else name for name in top_10_revenue['product_name']], fontsize=9)
ax1.set_xlabel('Estimated Revenue (₹ Billions)', fontsize=11, fontweight='bold')
ax1.set_title('Top 10 Products by Estimated Revenue', fontsize=13, fontweight='bold')
ax1.grid(axis='x', alpha=0.3)
for i, v in enumerate(top_10_revenue['estimated_revenue'].values / 1e9):
    ax1.text(v, i, f' ₹{v:.2f}B', va='center', fontsize=9, fontweight='bold')

# Top categories by product count
ax2 = fig.add_subplot(gs[1, 0])
top_cat_count = df['main_category'].value_counts().head(10)
top_cat_count.plot(kind='bar', ax=ax2, color='lightcoral', edgecolor='black')
ax2.set_xlabel('Category', fontsize=10, fontweight='bold')
ax2.set_ylabel('Product Count', fontsize=10, fontweight='bold')
ax2.set_title('Top 10 Categories by Product Count', fontsize=11, fontweight='bold')
ax2.set_xticklabels(ax2.get_xticklabels(), rotation=45, ha='right', fontsize=8)
ax2.grid(axis='y', alpha=0.3)

# Average rating by top categories
ax3 = fig.add_subplot(gs[1, 1])
top_cat_rating = df.groupby('main_category')['rating_clean'].mean().nlargest(10)
top_cat_rating.plot(kind='bar', ax=ax3, color='lightgreen', edgecolor='black')
ax3.set_xlabel('Category', fontsize=10, fontweight='bold')
ax3.set_ylabel('Average Rating', fontsize=10, fontweight='bold')
ax3.set_title('Top 10 Categories by Average Rating', fontsize=11, fontweight='bold')
ax3.set_xticklabels(ax3.get_xticklabels(), rotation=45, ha='right', fontsize=8)
ax3.set_ylim([0, 5])
ax3.axhline(y=4.0, color='red', linestyle='--', alpha=0.5, label='4.0 threshold')
ax3.legend()
ax3.grid(axis='y', alpha=0.3)

# Price vs Discount correlation
ax4 = fig.add_subplot(gs[2, 0])
sample_df2 = df.sample(min(300, len(df)))
scatter = ax4.scatter(sample_df2['actual_price_clean'], sample_df2['discount_pct_clean'], 
                     c=sample_df2['rating_clean'], cmap='RdYlGn', s=50, alpha=0.6, edgecolors='black', linewidth=0.5)
ax4.set_xlabel('Actual Price (₹)', fontsize=10, fontweight='bold')
ax4.set_ylabel('Discount %', fontsize=10, fontweight='bold')
ax4.set_title('Price vs Discount (colored by rating)', fontsize=11, fontweight='bold')
ax4.set_xscale('log')
ax4.grid(alpha=0.3)
cbar = plt.colorbar(scatter, ax=ax4)
cbar.set_label('Rating', fontsize=9)

# Revenue by price segment
ax5 = fig.add_subplot(gs[2, 1])
price_revenue = df.groupby('price_segment')['estimated_revenue'].sum().reindex(price_order) / 1e9
price_revenue.plot(kind='bar', ax=ax5, color='mediumpurple', edgecolor='black')
ax5.set_xlabel('Price Segment', fontsize=10, fontweight='bold')
ax5.set_ylabel('Estimated Revenue (₹ Billions)', fontsize=10, fontweight='bold')
ax5.set_title('Revenue by Price Segment', fontsize=11, fontweight='bold')
ax5.set_xticklabels(ax5.get_xticklabels(), rotation=45, ha='right', fontsize=8)
ax5.grid(axis='y', alpha=0.3)
for i, v in enumerate(price_revenue.values):
    ax5.text(i, v, f'₹{v:.1f}B', ha='center', va='bottom', fontsize=8, fontweight='bold')

plt.suptitle('Amazon Sales Analytics Dashboard', fontsize=16, fontweight='bold', y=0.995)
plt.savefig('/home/ubuntu/amazon_viz/05_dashboard.png', bbox_inches='tight')
plt.close()

print("\n✓ All visualizations created successfully!")
print(f"✓ Saved to: /home/ubuntu/amazon_viz/")
print("\nGenerated files:")
print("  1. 01_category_revenue.png")
print("  2. 02_price_analysis.png")
print("  3. 03_discount_analysis.png")
print("  4. 04_rating_analysis.png")
print("  5. 05_dashboard.png")
