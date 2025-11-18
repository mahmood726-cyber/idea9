"""
Figure 1 for Synthesis: MVMA Two-Stage Model and Borrowing Strength
Shows hierarchical structure and correlation-based information sharing
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Circle, Ellipse
import numpy as np

# Publication quality
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.size'] = 10
plt.rcParams['axes.linewidth'] = 1.0

fig = plt.figure(figsize=(12, 8))
ax = fig.add_subplot(111)
ax.set_xlim(0, 12)
ax.set_ylim(0, 10)
ax.axis('off')

# Title
ax.text(6, 9.7, 'Multivariate Meta-Analysis: Two-Stage Model and Borrowing Strength',
        ha='center', fontsize=13, fontweight='bold')

# ============ PANEL A: Two-Stage Hierarchical Model ============
ax.text(3, 9.0, 'A. Two-Stage Hierarchical Model', fontsize=11, fontweight='bold')

# Stage 1
stage1_box = FancyBboxPatch((0.5, 7.5), 5, 1.2, boxstyle="round,pad=0.1",
                           edgecolor='#2E86AB', facecolor='#A7C4D0', linewidth=2, alpha=0.3)
ax.add_patch(stage1_box)
ax.text(3, 8.5, 'Stage 1: Within-Study Model', ha='center', fontsize=10, fontweight='bold')
ax.text(3, 8.1, r'$\mathbf{y}_i | \boldsymbol{\mu}_i \sim N(\boldsymbol{\mu}_i, \mathbf{S}_i)$',
        ha='center', fontsize=11)
ax.text(0.7, 7.7, r'$\mathbf{y}_i$: observed effects', fontsize=8)
ax.text(0.7, 7.5, r'$\mathbf{S}_i$: within-study covariance (assumed known)', fontsize=8)

# Stage 2
stage2_box = FancyBboxPatch((0.5, 6.0), 5, 1.2, boxstyle="round,pad=0.1",
                           edgecolor='#A23B72', facecolor='#F18F01', linewidth=2, alpha=0.3)
ax.add_patch(stage2_box)
ax.text(3, 7.0, 'Stage 2: Between-Study Model', ha='center', fontsize=10, fontweight='bold')
ax.text(3, 6.6, r'$\boldsymbol{\mu}_i \sim N(\boldsymbol{\theta}, \boldsymbol{\Psi})$',
        ha='center', fontsize=11)
ax.text(0.7, 6.2, r'$\boldsymbol{\theta}$: pooled effects', fontsize=8)
ax.text(0.7, 6.0, r'$\boldsymbol{\Psi}$: between-study covariance', fontsize=8, color='#A23B72', fontweight='bold')

# Arrow between stages
arrow1 = FancyArrowPatch((3, 7.5), (3, 7.2),
                        arrowstyle='->', mutation_scale=25, linewidth=3, color='#555')
ax.add_patch(arrow1)

# Marginal
marginal_box = FancyBboxPatch((0.5, 4.5), 5, 1.2, boxstyle="round,pad=0.1",
                             edgecolor='#06A77D', facecolor='#D4F4DD', linewidth=2, alpha=0.4)
ax.add_patch(marginal_box)
ax.text(3, 5.5, 'Marginal Distribution', ha='center', fontsize=10, fontweight='bold')
ax.text(3, 5.1, r'$\mathbf{y}_i \sim N(\boldsymbol{\theta}, \mathbf{S}_i + \boldsymbol{\Psi})$',
        ha='center', fontsize=11)
ax.text(0.7, 4.7, 'Combines within + between study variation', fontsize=8, style='italic')

# Arrow to marginal
arrow2 = FancyArrowPatch((3, 6.0), (3, 5.7),
                        arrowstyle='->', mutation_scale=25, linewidth=3, color='#555')
ax.add_patch(arrow2)

# ============ PANEL B: Borrowing Strength Mechanism ============
ax.text(9, 9.0, 'B. Borrowing Strength', fontsize=11, fontweight='bold')

# Two correlated outcomes
outcome1_circ = Circle((7, 7.8), 0.6, edgecolor='#E63946', facecolor='#FFB3BA', linewidth=2, alpha=0.6)
ax.add_patch(outcome1_circ)
ax.text(7, 7.8, 'Outcome 1\n(precise)', ha='center', fontsize=8, fontweight='bold')
ax.text(7, 7.2, r'SE = 0.1', ha='center', fontsize=7, style='italic')

outcome2_circ = Circle((11, 7.8), 0.6, edgecolor='#457B9D', facecolor='#BAE1FF', linewidth=2, alpha=0.6)
ax.add_patch(outcome2_circ)
ax.text(11, 7.8, 'Outcome 2\n(imprecise)', ha='center', fontsize=8, fontweight='bold')
ax.text(11, 7.2, r'SE = 0.3', ha='center', fontsize=7, style='italic')

# Correlation arrow
corr_arrow = FancyArrowPatch((7.6, 7.8), (10.4, 7.8),
                            arrowstyle='<->', mutation_scale=20, linewidth=2.5,
                            color='#F77F00', linestyle='--')
ax.add_patch(corr_arrow)
ax.text(9, 8.1, r'$\rho = 0.6$', ha='center', fontsize=9, fontweight='bold',
        bbox=dict(boxstyle='round,pad=0.3', facecolor='#FFF3CD', edgecolor='#F77F00'))

# Information flow
info_box = FancyBboxPatch((6.5, 6.3), 5, 0.8, boxstyle="round,pad=0.08",
                         edgecolor='#06A77D', facecolor='#D4F4DD', linewidth=1.5)
ax.add_patch(info_box)
ax.text(9, 6.85, 'Information Sharing:', ha='center', fontsize=9, fontweight='bold')
ax.text(9, 6.5, 'Correlation enables Outcome 1 to improve Outcome 2 estimate',
        ha='center', fontsize=8)

# Efficiency gain
efficiency_box = FancyBboxPatch((6.5, 5.3), 5, 0.7, boxstyle="round,pad=0.08",
                               edgecolor='#2E86AB', facecolor='#E0F2F7', linewidth=1.5)
ax.add_patch(efficiency_box)
ax.text(9, 5.85, 'Result: Effective SE for Outcome 2', ha='center', fontsize=8, fontweight='bold')
ax.text(9, 5.5, r'$SE_{effective} < 0.3$ (shrinkage toward joint mean)',
        ha='center', fontsize=8, style='italic')

# ============ PANEL C: Between-Study Correlation Structure ============
ax.text(3, 4.0, 'C. Between-Study Covariance Matrix', fontsize=11, fontweight='bold')

# Psi matrix visualization
psi_box = FancyBboxPatch((0.8, 2.0), 4.4, 1.6, boxstyle="round,pad=0.08",
                        edgecolor='#A23B72', facecolor='white', linewidth=2)
ax.add_patch(psi_box)

ax.text(3, 3.4, r'$\boldsymbol{\Psi} = $', ha='center', fontsize=11, fontweight='bold', color='#A23B72')

# Matrix elements
ax.text(3, 2.95, r'$\begin{array}{cc}', ha='center', fontsize=10)
ax.text(2.2, 2.7, r'$\tau_1^2$', fontsize=10, color='#E63946', fontweight='bold')
ax.text(3.8, 2.7, r'$\rho \tau_1 \tau_2$', fontsize=10, color='#F77F00', fontweight='bold')
ax.text(2.2, 2.35, r'$\rho \tau_1 \tau_2$', fontsize=10, color='#F77F00', fontweight='bold')
ax.text(3.8, 2.35, r'$\tau_2^2$', fontsize=10, color='#457B9D', fontweight='bold')

# Labels
ax.text(0.9, 2.7, 'Heterogeneity', fontsize=7, rotation=90, va='center', color='#E63946')
ax.text(4.8, 2.7, 'Heterogeneity', fontsize=7, rotation=90, va='center', color='#457B9D')
ax.text(3, 2.05, 'Between-study correlation', fontsize=7, ha='center', color='#F77F00', fontweight='bold')

# ============ PANEL D: Key Parameters ============
ax.text(9, 4.0, 'D. Critical Parameters', fontsize=11, fontweight='bold')

# Sample size requirement
param1_box = FancyBboxPatch((6.5, 3.2), 5, 0.5, boxstyle="round,pad=0.05",
                           edgecolor='#2E86AB', facecolor='#E0F2F7', linewidth=1.5)
ax.add_patch(param1_box)
ax.text(6.7, 3.55, '• Sample Size:', fontsize=8, fontweight='bold')
ax.text(8.2, 3.55, r'$k \geq 2p$ (rule of thumb)', fontsize=8)
ax.text(6.8, 3.3, r'   $k$ = studies, $p$ = outcomes', fontsize=7, style='italic')

# Correlation requirement
param2_box = FancyBboxPatch((6.5, 2.5), 5, 0.5, boxstyle="round,pad=0.05",
                           edgecolor='#F77F00', facecolor='#FFF9E3', linewidth=1.5)
ax.add_patch(param2_box)
ax.text(6.7, 2.85, '• Within-Study Correlation:', fontsize=8, fontweight='bold')
ax.text(9.3, 2.85, 'Often unknown', fontsize=8, color='#D62828')
ax.text(6.8, 2.6, '   Sensitivity analysis essential (try ρ = 0, 0.3, 0.6)', fontsize=7, style='italic')

# Between-study correlation
param3_box = FancyBboxPatch((6.5, 1.8), 5, 0.5, boxstyle="round,pad=0.05",
                           edgecolor='#A23B72', facecolor='#F9E6F2', linewidth=1.5)
ax.add_patch(param3_box)
ax.text(6.7, 2.15, '• Between-Study Correlation:', fontsize=8, fontweight='bold')
ax.text(9.8, 2.15, r'$\rho$ estimated', fontsize=8)
ax.text(6.8, 1.9, r'   Positive: effects vary together; Negative: opposing patterns', fontsize=7, style='italic')

# Degrees of freedom
param4_box = FancyBboxPatch((6.5, 1.1), 5, 0.5, boxstyle="round,pad=0.05",
                           edgecolor='#06A77D', facecolor='#D4F4DD', linewidth=1.5)
ax.add_patch(param4_box)
ax.text(6.7, 1.45, '• Degrees of Freedom:', fontsize=8, fontweight='bold')
ax.text(9.0, 1.45, r'$df \approx k - p$', fontsize=8)
ax.text(6.8, 1.2, '   Use Hartung-Knapp adjustment for small k', fontsize=7, style='italic')

# Footer caption
ax.text(6, 0.4, 'Figure 1. The two-stage hierarchical model (A) forms the foundation of MVMA. Borrowing strength (B) occurs when\n' +
        'correlated outcomes share information, improving precision. The between-study covariance matrix Ψ (C) captures both\n' +
        'heterogeneity (diagonal) and correlation (off-diagonal). Critical parameters (D) include sample size (k ≥ 2p) and correlations.',
        ha='center', fontsize=7.5, style='italic', multialignment='center')

plt.tight_layout()
plt.savefig('/home/user/idea9/synthesis_figures/figure1_synthesis.png', dpi=300, bbox_inches='tight')
plt.savefig('/home/user/idea9/synthesis_figures/figure1_synthesis.pdf', bbox_inches='tight')
print("Figure 1 (Synthesis) saved successfully!")
plt.close()
