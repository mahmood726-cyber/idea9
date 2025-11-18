"""
Figure 1: Multivariate Meta-Analysis Framework
Conceptual diagram showing how multiple studies contribute to correlated outcomes
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Circle, Ellipse
import numpy as np

# Set publication-quality style
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Arial']
plt.rcParams['font.size'] = 10
plt.rcParams['axes.linewidth'] = 1.0
plt.rcParams['xtick.major.width'] = 1.0
plt.rcParams['ytick.major.width'] = 1.0

fig, ax = plt.subplots(figsize=(10, 8))
ax.set_xlim(0, 10)
ax.set_ylim(0, 10)
ax.axis('off')

# Title
ax.text(5, 9.5, 'Multivariate Meta-Analysis Framework',
        ha='center', va='top', fontsize=14, fontweight='bold')

# Color scheme
color_study = '#4ECDC4'
color_outcome1 = '#FF6B6B'
color_outcome2 = '#4ECDC4'
color_pooled = '#95E1D3'
color_between = '#F38181'

# Part A: Individual Studies (Left side)
ax.text(2.5, 8.5, 'A. Individual Studies', ha='center', fontsize=11, fontweight='bold')

# Study 1
study1_box = FancyBboxPatch((0.5, 7.2), 1.8, 0.8, boxstyle="round,pad=0.05",
                            edgecolor='black', facecolor=color_study, linewidth=1.5, alpha=0.3)
ax.add_patch(study1_box)
ax.text(1.4, 7.6, 'Study 1', ha='center', fontsize=9, fontweight='bold')
ax.text(1.4, 7.35, r'$\mathbf{y}_1$', ha='center', fontsize=8)

# Study 2
study2_box = FancyBboxPatch((2.5, 7.2), 1.8, 0.8, boxstyle="round,pad=0.05",
                            edgecolor='black', facecolor=color_study, linewidth=1.5, alpha=0.3)
ax.add_patch(study2_box)
ax.text(3.4, 7.6, 'Study 2', ha='center', fontsize=9, fontweight='bold')
ax.text(3.4, 7.35, r'$\mathbf{y}_2$', ha='center', fontsize=8)

# Study k (with dots)
ax.text(2.5, 6.7, '...', ha='center', fontsize=12)

study_k_box = FancyBboxPatch((1.3, 5.9), 2.4, 0.8, boxstyle="round,pad=0.05",
                             edgecolor='black', facecolor=color_study, linewidth=1.5, alpha=0.3)
ax.add_patch(study_k_box)
ax.text(2.5, 6.3, 'Study k', ha='center', fontsize=9, fontweight='bold')
ax.text(2.5, 6.05, r'$\mathbf{y}_k$', ha='center', fontsize=8)

# Outcome representation
ax.text(0.3, 5.3, 'Each study reports:', fontsize=8, style='italic')
ax.text(0.3, 4.95, '• Outcome 1 (e.g., efficacy)', fontsize=7, color=color_outcome1)
ax.text(0.3, 4.7, '• Outcome 2 (e.g., safety)', fontsize=7, color=color_outcome2)
ax.text(0.3, 4.45, r'• Within-study covariance $\mathbf{S}_i$', fontsize=7)

# Part B: Multivariate Model (Center)
ax.text(5, 8.5, 'B. Multivariate Random-Effects Model', ha='center', fontsize=11, fontweight='bold')

# Model box
model_box = FancyBboxPatch((4, 6.5), 2, 1.8, boxstyle="round,pad=0.1",
                          edgecolor='black', facecolor='#FFF9E3', linewidth=2)
ax.add_patch(model_box)

# Model equations
ax.text(5, 8.0, r'$\mathbf{y}_i \sim N(\boldsymbol{\theta}, \mathbf{V}_i)$',
        ha='center', fontsize=10, fontweight='bold')
ax.text(5, 7.6, r'where:', ha='center', fontsize=8)
ax.text(5, 7.3, r'$\mathbf{V}_i = \mathbf{S}_i + \boldsymbol{\Psi}$', ha='center', fontsize=9)

# Within-study variance
ax.text(5, 6.9, r'$\mathbf{S}_i$: Within-study', ha='center', fontsize=7.5)
ax.text(5, 6.65, 'covariance (known)', ha='center', fontsize=7.5)

# Between-study variance
ax.text(5, 6.35, r'$\boldsymbol{\Psi}$: Between-study', ha='center', fontsize=7.5, color=color_between)
ax.text(5, 6.1, 'covariance (estimated)', ha='center', fontsize=7.5, color=color_between)

# Between-study covariance matrix visualization
psi_box = FancyBboxPatch((4.1, 4.8), 1.8, 1.1, boxstyle="round,pad=0.05",
                        edgecolor=color_between, facecolor='white', linewidth=1.5)
ax.add_patch(psi_box)
# Matrix representation as text (matplotlib mathtext doesn't support full LaTeX matrices)
ax.text(5, 5.85, r'$\boldsymbol{\Psi} = $', ha='center', fontsize=9, color=color_between, fontweight='bold')
ax.text(5, 5.55, r'$\left[\tau_1^2,\ \rho\tau_1\tau_2;\ \rho\tau_1\tau_2,\ \tau_2^2\right]$',
        ha='center', fontsize=8, color=color_between)
ax.text(5, 5.3, r'$\tau^2$: heterogeneity', ha='center', fontsize=7)
ax.text(5, 5.05, r'$\rho$: between-study correlation', ha='center', fontsize=7, fontweight='bold')

# Part C: Pooled Estimates (Right side)
ax.text(7.8, 8.5, 'C. Pooled Estimates', ha='center', fontsize=11, fontweight='bold')

# Pooled effect box
pooled_box = FancyBboxPatch((6.9, 7.0), 1.8, 1.2, boxstyle="round,pad=0.1",
                           edgecolor='black', facecolor=color_pooled, linewidth=2, alpha=0.4)
ax.add_patch(pooled_box)
ax.text(7.8, 7.9, r'$\boldsymbol{\theta}$', ha='center', fontsize=11, fontweight='bold')
ax.text(7.8, 7.55, 'Pooled Effects', ha='center', fontsize=9)
ax.text(7.8, 7.3, r'$\theta_1$: Outcome 1', ha='center', fontsize=8, color=color_outcome1)
ax.text(7.8, 7.1, r'$\theta_2$: Outcome 2', ha='center', fontsize=8, color=color_outcome2)

# Key advantages
advantages_box = FancyBboxPatch((6.5, 4.5), 2.6, 2.2, boxstyle="round,pad=0.08",
                               edgecolor='#555', facecolor='#F0F0F0', linewidth=1, linestyle='--')
ax.add_patch(advantages_box)
ax.text(7.8, 6.5, 'Key Advantages', ha='center', fontsize=9, fontweight='bold')
ax.text(6.6, 6.2, '1. Borrowing strength:', fontsize=7.5, fontweight='bold')
ax.text(6.75, 5.95, 'Information from one outcome', fontsize=7)
ax.text(6.75, 5.75, 'improves estimates of others', fontsize=7)

ax.text(6.6, 5.45, '2. Missing data handling:', fontsize=7.5, fontweight='bold')
ax.text(6.75, 5.2, 'Studies with partial outcomes', fontsize=7)
ax.text(6.75, 5.0, 'contribute via correlation', fontsize=7)

ax.text(6.6, 4.7, '3. Efficiency gains:', fontsize=7.5, fontweight='bold')
ax.text(6.75, 4.45, '15-30% narrower CIs when', fontsize=7)
ax.text(6.75, 4.25, r'$\rho > 0.3$', fontsize=7)

# Arrows showing flow
# Studies to model
arrow1 = FancyArrowPatch((2.5, 6.3), (4, 7.3),
                        arrowstyle='->', mutation_scale=20, linewidth=2, color='gray')
ax.add_patch(arrow1)

# Model to pooled estimates
arrow2 = FancyArrowPatch((6, 7.4), (6.9, 7.6),
                        arrowstyle='->', mutation_scale=20, linewidth=2, color='gray')
ax.add_patch(arrow2)

# Part D: Comparison (Bottom)
ax.text(5, 3.8, 'D. Multivariate vs. Univariate Meta-Analysis',
        ha='center', fontsize=11, fontweight='bold')

# Comparison table
table_data = [
    ['', 'Univariate MA', 'Multivariate MA'],
    ['Outcomes analyzed', 'Separately', 'Jointly'],
    ['Correlation modeled', 'No', r'Yes ($\rho$ estimated)'],
    ['Missing outcomes', 'Excluded or imputed', 'Contribute via $\\rho$'],
    ['Precision', 'Lower', 'Higher (borrows strength)'],
    ['Inference', 'Separate for each', 'Joint across outcomes']
]

# Create table manually
col_widths = [2.2, 1.8, 2.0]
row_height = 0.35
start_x = 2.5
start_y = 3.4

# Header row
for j, (width, text) in enumerate(zip(col_widths, table_data[0])):
    x = start_x + sum(col_widths[:j])
    if j == 0:
        ax.text(x + width/2, start_y, text, ha='center', fontsize=8, fontweight='bold')
    else:
        box = FancyBboxPatch((x, start_y - 0.15), width, row_height,
                            boxstyle="round,pad=0.02", edgecolor='black',
                            facecolor='lightgray', linewidth=1)
        ax.add_patch(box)
        ax.text(x + width/2, start_y, text, ha='center', fontsize=8, fontweight='bold')

# Data rows
for i, row in enumerate(table_data[1:], 1):
    y = start_y - i * row_height
    for j, (width, text) in enumerate(zip(col_widths, row)):
        x = start_x + sum(col_widths[:j])
        if j == 0:
            ax.text(x + width/2, y, text, ha='center', fontsize=7, style='italic')
        elif j == 1:
            box = FancyBboxPatch((x, y - 0.15), width, row_height,
                                boxstyle="round,pad=0.02", edgecolor='gray',
                                facecolor='#FFE5E5', linewidth=0.5, alpha=0.5)
            ax.add_patch(box)
            ax.text(x + width/2, y, text, ha='center', fontsize=7)
        else:
            box = FancyBboxPatch((x, y - 0.15), width, row_height,
                                boxstyle="round,pad=0.02", edgecolor='gray',
                                facecolor='#E5FFE5', linewidth=0.5, alpha=0.5)
            ax.add_patch(box)
            ax.text(x + width/2, y, text, ha='center', fontsize=7)

# Footer note
ax.text(5, 0.5, 'Figure 1. Conceptual framework for multivariate meta-analysis showing individual studies (A), '+
        'the multivariate random-effects model (B),\npooled estimates with key advantages (C), and comparison with univariate approaches (D).',
        ha='center', fontsize=7.5, style='italic', wrap=True)

plt.tight_layout()
plt.savefig('/home/user/idea9/figures/figure1_mvma_framework.png', dpi=300, bbox_inches='tight')
plt.savefig('/home/user/idea9/figures/figure1_mvma_framework.pdf', bbox_inches='tight')
print("Figure 1 saved successfully!")
plt.close()
