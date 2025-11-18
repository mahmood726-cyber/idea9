"""
Figure 2: Multivariate Meta-Analysis Method Selection and Estimation Flowchart
Decision tree and method comparison for MVMA
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Circle, Rectangle
import numpy as np

# Set publication-quality style
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Arial']
plt.rcParams['font.size'] = 9
plt.rcParams['axes.linewidth'] = 1.0

fig = plt.figure(figsize=(12, 10))

# Create main axis
ax = fig.add_subplot(111)
ax.set_xlim(0, 12)
ax.set_ylim(0, 11)
ax.axis('off')

# Title
ax.text(6, 10.5, 'Multivariate Meta-Analysis: Method Selection and Estimation',
        ha='center', va='top', fontsize=13, fontweight='bold')

# Color scheme
color_decision = '#FFE5CC'
color_method = '#CCE5FF'
color_recommendation = '#E5FFCC'
color_warning = '#FFE5E5'

# ============ PART A: Decision Flowchart ============
ax.text(3, 10, 'A. Method Selection Decision Tree', fontsize=11, fontweight='bold')

# Start: Multiple outcomes?
start_box = FancyBboxPatch((2, 9.0), 2, 0.6, boxstyle="round,pad=0.08",
                          edgecolor='black', facecolor='#C0C0C0', linewidth=2)
ax.add_patch(start_box)
ax.text(3, 9.3, 'Multiple correlated\noutcomes?', ha='center', fontsize=8, fontweight='bold')

# Decision 1: Yes/No
arrow_yes1 = FancyArrowPatch((3, 9.0), (3, 8.3),
                           arrowstyle='->', mutation_scale=15, linewidth=1.5, color='green')
ax.add_patch(arrow_yes1)
ax.text(3.2, 8.65, 'Yes', fontsize=7, color='green', fontweight='bold')

arrow_no1 = FancyArrowPatch((4, 9.3), (5.5, 9.3),
                          arrowstyle='->', mutation_scale=15, linewidth=1.5, color='red')
ax.add_patch(arrow_no1)
ax.text(4.7, 9.5, 'No', fontsize=7, color='red', fontweight='bold')

# No path: Univariate MA
univariate_box = FancyBboxPatch((5.5, 9.0), 1.8, 0.6, boxstyle="round,pad=0.05",
                               edgecolor='black', facecolor=color_warning, linewidth=1.5)
ax.add_patch(univariate_box)
ax.text(6.4, 9.3, 'Use standard\nunivariate MA', ha='center', fontsize=7)

# Box 2: Within-study correlations available?
box2 = FancyBboxPatch((2, 7.7), 2, 0.6, boxstyle="round,pad=0.08",
                     edgecolor='black', facecolor=color_decision, linewidth=1.5)
ax.add_patch(box2)
ax.text(3, 8.0, 'Within-study\ncorrelations known?', ha='center', fontsize=8)

# Decision 2
arrow_yes2 = FancyArrowPatch((3, 7.7), (3, 7.0),
                           arrowstyle='->', mutation_scale=15, linewidth=1.5, color='green')
ax.add_patch(arrow_yes2)
ax.text(3.2, 7.35, 'Yes', fontsize=7, color='green', fontweight='bold')

arrow_no2 = FancyArrowPatch((4, 8.0), (5.5, 8.0),
                          arrowstyle='->', mutation_scale=15, linewidth=1.5, color='orange')
ax.add_patch(arrow_no2)
ax.text(4.5, 8.15, 'No/Partial', fontsize=7, color='orange', fontweight='bold')

# No path: Sensitivity analysis
sensitivity_box = FancyBboxPatch((5.5, 7.7), 1.8, 0.6, boxstyle="round,pad=0.05",
                                edgecolor='orange', facecolor='#FFF9E3', linewidth=1.5)
ax.add_patch(sensitivity_box)
ax.text(6.4, 8.0, 'Assume ρ = 0, 0.5\nSensitivity analysis', ha='center', fontsize=7)

# Box 3: Missing outcomes?
box3 = FancyBboxPatch((2, 6.4), 2, 0.6, boxstyle="round,pad=0.08",
                     edgecolor='black', facecolor=color_decision, linewidth=1.5)
ax.add_patch(box3)
ax.text(3, 6.7, 'Missing outcome\ndata present?', ha='center', fontsize=8)

# Decision 3
arrow_yes3 = FancyArrowPatch((2.5, 6.4), (1.5, 5.8),
                           arrowstyle='->', mutation_scale=15, linewidth=1.5, color='green')
ax.add_patch(arrow_yes3)
ax.text(1.9, 6.1, 'Yes', fontsize=7, color='green', fontweight='bold')

arrow_no3 = FancyArrowPatch((3.5, 6.4), (4.5, 5.8),
                          arrowstyle='->', mutation_scale=15, linewidth=1.5, color='blue')
ax.add_patch(arrow_no3)
ax.text(4.1, 6.1, 'No', fontsize=7, color='blue', fontweight='bold')

# Missing data path
missing_box = FancyBboxPatch((0.3, 5.2), 2.4, 0.6, boxstyle="round,pad=0.05",
                            edgecolor='green', facecolor=color_method, linewidth=1.5)
ax.add_patch(missing_box)
ax.text(1.5, 5.5, 'MVMA with MI or\nPattern Mixture Model', ha='center', fontsize=7.5, fontweight='bold')

# Complete data path
complete_box = FancyBboxPatch((3.7, 5.2), 2.4, 0.6, boxstyle="round,pad=0.05",
                             edgecolor='blue', facecolor=color_method, linewidth=1.5)
ax.add_patch(complete_box)
ax.text(4.9, 5.5, 'Standard MVMA\n(REML/ML/Bayesian)', ha='center', fontsize=7.5, fontweight='bold')

# Box 4: Network structure?
box4 = FancyBboxPatch((2, 4.6), 2, 0.6, boxstyle="round,pad=0.08",
                     edgecolor='black', facecolor=color_decision, linewidth=1.5)
ax.add_patch(box4)
ax.text(3, 4.9, 'Network meta-analysis\n(multiple treatments)?', ha='center', fontsize=8)

# Decision 4
arrow_yes4 = FancyArrowPatch((3, 4.6), (3, 3.9),
                           arrowstyle='->', mutation_scale=15, linewidth=1.5, color='green')
ax.add_patch(arrow_yes4)
ax.text(3.2, 4.25, 'Yes', fontsize=7, color='green', fontweight='bold')

arrow_no4 = FancyArrowPatch((4, 4.9), (5.5, 4.9),
                          arrowstyle='->', mutation_scale=15, linewidth=1.5, color='blue')
ax.add_patch(arrow_no4)
ax.text(4.7, 5.05, 'No', fontsize=7, color='blue', fontweight='bold')

# Network path
network_box = FancyBboxPatch((2, 3.3), 2, 0.6, boxstyle="round,pad=0.05",
                            edgecolor='purple', facecolor='#E5CCFF', linewidth=2)
ax.add_patch(network_box)
ax.text(3, 3.6, 'Multivariate\nNetwork MA', ha='center', fontsize=8, fontweight='bold', color='purple')

# Pairwise path
pairwise_box = FancyBboxPatch((5.5, 4.6), 1.8, 0.6, boxstyle="round,pad=0.05",
                             edgecolor='blue', facecolor=color_recommendation, linewidth=1.5)
ax.add_patch(pairwise_box)
ax.text(6.4, 4.9, 'Pairwise MVMA', ha='center', fontsize=8, fontweight='bold')

# ============ PART B: Estimation Method Comparison ============
ax.text(9, 10, 'B. Estimation Method Comparison', fontsize=11, fontweight='bold')

# REML Box
reml_box = FancyBboxPatch((7.5, 8.7), 2.2, 1.1, boxstyle="round,pad=0.08",
                         edgecolor='black', facecolor='#E3F2FD', linewidth=1.5)
ax.add_patch(reml_box)
ax.text(8.6, 9.6, 'REML', ha='center', fontsize=10, fontweight='bold')
ax.text(7.6, 9.3, '✓ Unbiased τ² estimates', fontsize=7)
ax.text(7.6, 9.05, '✓ Recommended default', fontsize=7)
ax.text(7.6, 8.8, '• Best for k < 20', fontsize=7, style='italic')

# ML Box
ml_box = FancyBboxPatch((10, 8.7), 2.2, 1.1, boxstyle="round,pad=0.08",
                       edgecolor='black', facecolor='#FFF3E0', linewidth=1.5)
ax.add_patch(ml_box)
ax.text(11.1, 9.6, 'ML', ha='center', fontsize=10, fontweight='bold')
ax.text(10.1, 9.3, '✓ Model comparison (LRT)', fontsize=7)
ax.text(10.1, 9.05, '✓ Fast convergence', fontsize=7)
ax.text(10.1, 8.8, '• Biased τ² (small k)', fontsize=7, style='italic')

# Bayesian Box
bayesian_box = FancyBboxPatch((7.5, 7.3), 2.2, 1.1, boxstyle="round,pad=0.08",
                             edgecolor='black', facecolor='#F1F8E9', linewidth=1.5)
ax.add_patch(bayesian_box)
ax.text(8.6, 8.2, 'Bayesian (MCMC)', ha='center', fontsize=10, fontweight='bold')
ax.text(7.6, 7.9, '✓ Full posterior distributions', fontsize=7)
ax.text(7.6, 7.65, '✓ Treatment rankings', fontsize=7)
ax.text(7.6, 7.4, '• Requires prior specification', fontsize=7, style='italic')

# Multiple Imputation Box
mi_box = FancyBboxPatch((10, 7.3), 2.2, 1.1, boxstyle="round,pad=0.08",
                       edgecolor='black', facecolor='#E8F5E9', linewidth=1.5)
ax.add_patch(mi_box)
ax.text(11.1, 8.2, 'Multiple Imputation', ha='center', fontsize=10, fontweight='bold')
ax.text(10.1, 7.9, '✓ Handles missing data', fontsize=7)
ax.text(10.1, 7.65, '✓ Valid under MAR', fontsize=7)
ax.text(10.1, 7.4, '• Requires M imputations', fontsize=7, style='italic')

# ============ PART C: Performance Characteristics ============
ax.text(9, 6.7, 'C. Performance Summary (from Simulation Studies)', fontsize=11, fontweight='bold')

# Performance table
table_y_start = 6.3
table_x_start = 7.5

# Headers
headers = ['Method', 'Bias', 'Coverage', 'Efficiency', 'Complexity']
col_widths = [1.2, 0.7, 0.9, 0.8, 1.0]

# Draw headers
for i, (header, width) in enumerate(zip(headers, col_widths)):
    x = table_x_start + sum(col_widths[:i])
    box = Rectangle((x, table_y_start - 0.05), width, 0.35,
                    edgecolor='black', facecolor='#BDBDBD', linewidth=1)
    ax.add_patch(box)
    ax.text(x + width/2, table_y_start + 0.12, header, ha='center',
           fontsize=7, fontweight='bold')

# Data rows
methods_data = [
    ['REML', '++', '++', '+', 'Low'],
    ['ML', '+', '+', '++', 'Low'],
    ['Bayesian', '++', '++', '++', 'High'],
    ['MI (MAR)', '++', '++', '+', 'Medium']
]

row_colors = ['#E3F2FD', '#FFF3E0', '#F1F8E9', '#E8F5E9']

for row_idx, (row_data, row_color) in enumerate(zip(methods_data, row_colors)):
    y = table_y_start - (row_idx + 1) * 0.35
    for col_idx, (cell, width) in enumerate(zip(row_data, col_widths)):
        x = table_x_start + sum(col_widths[:col_idx])
        box = Rectangle((x, y - 0.05), width, 0.35,
                       edgecolor='gray', facecolor=row_color, linewidth=0.5, alpha=0.6)
        ax.add_patch(box)
        ax.text(x + width/2, y + 0.12, cell, ha='center', fontsize=7)

# Legend for performance indicators
ax.text(7.6, 4.75, '++ Excellent    + Good', fontsize=6.5, style='italic', color='#555')

# ============ PART D: Recommendations ============
ax.text(3, 2.7, 'D. Practical Recommendations', fontsize=11, fontweight='bold')

# Recommendation boxes
rec1 = FancyBboxPatch((0.5, 1.8), 3.5, 0.7, boxstyle="round,pad=0.08",
                     edgecolor='green', facecolor=color_recommendation, linewidth=1.5)
ax.add_patch(rec1)
ax.text(0.6, 2.35, '1. Small meta-analyses (k < 10):', fontsize=8, fontweight='bold')
ax.text(0.75, 2.1, '→ Use REML for unbiased variance estimates', fontsize=7)
ax.text(0.75, 1.9, '→ Consider Bayesian for weakly informative priors', fontsize=7)

rec2 = FancyBboxPatch((4.3, 1.8), 3.5, 0.7, boxstyle="round,pad=0.08",
                     edgecolor='blue', facecolor=color_recommendation, linewidth=1.5)
ax.add_patch(rec2)
ax.text(4.4, 2.35, '2. Missing outcome data:', fontsize=8, fontweight='bold')
ax.text(4.55, 2.1, '→ Multiple imputation if MAR plausible', fontsize=7)
ax.text(4.55, 1.9, '→ Pattern mixture models for sensitivity to MNAR', fontsize=7)

rec3 = FancyBboxPatch((8.0, 1.8), 3.8, 0.7, boxstyle="round,pad=0.08",
                     edgecolor='purple', facecolor=color_recommendation, linewidth=1.5)
ax.add_patch(rec3)
ax.text(8.1, 2.35, '3. Network meta-analysis:', fontsize=8, fontweight='bold')
ax.text(8.25, 2.1, '→ Bayesian for treatment rankings & probabilities', fontsize=7)
ax.text(8.25, 1.9, '→ Check inconsistency with node-splitting', fontsize=7)

rec4 = FancyBboxPatch((0.5, 0.9), 3.5, 0.7, boxstyle="round,pad=0.08",
                     edgecolor='orange', facecolor=color_recommendation, linewidth=1.5)
ax.add_patch(rec4)
ax.text(0.6, 1.45, '4. Unknown within-study correlations:', fontsize=8, fontweight='bold')
ax.text(0.75, 1.2, '→ Assume ρ = 0 (conservative)', fontsize=7)
ax.text(0.75, 1.0, '→ Sensitivity: ρ ∈ {0, 0.3, 0.6}', fontsize=7)

rec5 = FancyBboxPatch((4.3, 0.9), 3.5, 0.7, boxstyle="round,pad=0.08",
                     edgecolor='red', facecolor='#FFE5E5', linewidth=1.5)
ax.add_patch(rec5)
ax.text(4.4, 1.45, '5. When NOT to use MVMA:', fontsize=8, fontweight='bold')
ax.text(4.55, 1.2, '→ Outcomes truly independent (ρ ≈ 0)', fontsize=7)
ax.text(4.55, 1.0, '→ Very small k (< 5) with complex structure', fontsize=7)

rec6 = FancyBboxPatch((8.0, 0.9), 3.8, 0.7, boxstyle="round,pad=0.08",
                     edgecolor='teal', facecolor=color_recommendation, linewidth=1.5)
ax.add_patch(rec6)
ax.text(8.1, 1.45, '6. Large meta-analyses (k > 50):', fontsize=8, fontweight='bold')
ax.text(8.25, 1.2, '→ REML and ML converge; ML faster', fontsize=7)
ax.text(8.25, 1.0, '→ Consider variance structure constraints', fontsize=7)

# Footer
ax.text(6, 0.3, 'Figure 2. Method selection decision tree (A), estimation method comparison (B), performance summary (C),\n'+
        'and practical recommendations (D) for multivariate meta-analysis.',
        ha='center', fontsize=7.5, style='italic')

plt.tight_layout()
plt.savefig('/home/user/idea9/figures/figure2_method_flowchart.png', dpi=300, bbox_inches='tight')
plt.savefig('/home/user/idea9/figures/figure2_method_flowchart.pdf', bbox_inches='tight')
print("Figure 2 saved successfully!")
plt.close()
