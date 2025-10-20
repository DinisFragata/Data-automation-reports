import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Configurations of charts
sns.set_style("whitegrid")
plt.rcParams.update({
    'font.size': 12,
    'axes.titlesize': 14,
    'axes.labelsize': 12
})

def generate_charts(df):
    # Create column for Revenue
    df['Revenue'] = df['Quantity'] * df['Price']
    
    os.makedirs('assets', exist_ok=True)
    
    # Total Quantity per Product
    qty_product = df.groupby('Product')['Quantity'].sum().reset_index()
    plt.figure(figsize=(8,5))
    bar1 = sns.barplot(data=qty_product, hue='Product', y='Quantity', palette='Blues_d', legend=False )
    plt.title('Total Quantity per Product', fontsize=14, weight='bold')
    plt.xlabel('Product')
    plt.ylabel('Quantity')
    # Values above the bars
    for p in bar1.patches:
        bar1.annotate(f'{int(p.get_height())}', 
                      (p.get_x() + p.get_width() / 2., p.get_height()), 
                      ha='center', va='bottom', fontsize=10)
    plt.tight_layout()
    plt.savefig('assets/total_quantity_per_product.png', dpi=300)
    plt.close()
    
    # Total Revenue per Product
    revenue_product = df.groupby('Product')['Revenue'].sum().reset_index()
    plt.figure(figsize=(8,5))
    bar2 = sns.barplot(data=revenue_product, hue='Product', y='Revenue', palette='Purples_d', legend=False)
    plt.title('Total Revenue per Product', fontsize=14, weight='bold')
    plt.xlabel('Product')
    plt.ylabel('Revenue ($)')
    for p in bar2.patches:
        bar2.annotate(f'${p.get_height():.2f}', 
                      (p.get_x() + p.get_width() / 2., p.get_height()), 
                      ha='center', va='bottom', fontsize=10)
    plt.tight_layout()
    plt.savefig('assets/total_revenue_per_product.png', dpi=300)
    plt.close()
    
    # Total Quantity per Seller
    qty_seller = df.groupby('Seller')['Quantity'].sum().reset_index()
    plt.figure(figsize=(8,5))
    bar3 = sns.barplot(data=qty_seller, hue='Seller', y='Quantity', palette='Greens_d', legend=False)
    plt.title('Total Quantity per Seller', fontsize=14, weight='bold')
    plt.xlabel('Seller')
    plt.ylabel('Quantity')
    for p in bar3.patches:
        bar3.annotate(f'{int(p.get_height())}', 
                      (p.get_x() + p.get_width() / 2., p.get_height()), 
                      ha='center', va='bottom', fontsize=10)
    plt.tight_layout()
    plt.savefig('assets/total_quantity_per_seller.png', dpi=300)
    plt.close()
    
    # Trend: Quantity over Time
    trend = df.groupby('Date')['Quantity'].sum().reset_index()
    plt.figure(figsize=(10,5))
    sns.lineplot(data=trend, x='Date', y='Quantity', marker='o', color='teal', linewidth=2)
    plt.title('Quantity Trend over Time', fontsize=14, weight='bold')
    plt.xlabel('Date')
    plt.ylabel('Quantity')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('assets/quantity_trend_over_time.png', dpi=300)
    plt.close()