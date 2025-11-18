"""
Figure 2 for Synthesis: MVMA Application Guide and Sample Size Requirements
Decision framework and practical considerations
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle, Polygon
import numpy as np

# Publication quality
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.size'] = 9
plt.rcParams['axes.linewidth'] = 1.0

fig = plt.figure(figsize=(12, 10))
ax = fig.add_subplot(111)
ax.set_xlim(0, 12)
ax.set_ylim(0, 11)
ax.axis('off')

# Title
ax.text(6, 10.6, 'Multivariate Meta-Analysis: Decision Framework and Requirements',
        ha='center', fontsize=13, fontweight='bold')

# ============ PANEL A: When to Use MVMA ============
ax.text(3, 10.1, 'A. When to Use MVMA', fontsize=11, fontweight='bold')

# Recommended
rec_box = FancyBboxPatch((0.3, 8.5), 5.4, 1.4, boxstyle="round,pad=0.1",
                        edgecolor='#06A77D', facecolor='#D4F4DD', linewidth=2)
ax.add_patch(rec_box)
ax.text(3, 9.75, '✓ MVMA Recommended When:', ha='center', fontsize=10, fontweight='bold', color='#06A77D')
ax.text(0.5, 9.45, '• Outcomes conceptually related and likely correlated', fontsize=8)
ax.text(0.5, 9.2, '• Missing outcomes differ by study', fontsize=8)
ax.text(0.5, 8.95, r'• Sample size adequate ($k \geq 2p$)', fontsize=8)
ax.text(0.5, 8.7, '• Joint inference scientifically meaningful', fontsize=8)

# Not recommended
notrec_box = FancyBboxPatch((0.3, 6.9), 5.4, 1.4, boxstyle="round,pad=0.1",
                           edgecolor='#E63946', facecolor='#FFE5E7', linewidth=2)
ax.add_patch(notrec_box)
ax.text(3, 8.15, '✗ MVMA Unreliable When:', ha='center', fontsize=10, fontweight='bold', color='#E63946')
ax.text(0.5, 7.85, r'• Too few studies ($k < 2p$)', fontsize=8)
ax.text(0.5, 7.6, r'• Outcomes independent ($\rho \approx 0$)', fontsize=8)
ax.text(0.5, 7.35, '• Within-study correlations unknown and misspecified', fontsize=8)
ax.text(0.5, 7.1, r'• Extreme heterogeneity ($I^2 > 90\%$) with small $k$', fontsize=8)

# ============ PANEL B: Sample Size Requirements ============
ax.text(9, 10.1, 'B. Sample Size Requirements', fontsize=11, fontweight='bold')

# k vs p plot
plot_box = Rectangle((6.5, 8.5), 5, 1.5, edgecolor='#2E86AB', facecolor='white', linewidth=2)
ax.add_patch(plot_box)

# Create mini plot
k_values = np.array([5, 10, 15, 20, 25, 30])
p_values = k_values / 2  # k = 2p line

# Safe zone (k >= 2p)
safe_zone = Polygon([(6.5, 8.5), (11.5, 8.5), (11.5, 10), (9.5, 10), (6.5, 9.25)],
                   facecolor='#D4F4DD', alpha=0.5, edgecolor='none')
ax.add_patch(safe_zone)

# Caution zone
caution_zone = Polygon([(6.5, 8.5), (6.5, 9.25), (9.5, 10), (6.5, 10)],
                      facecolor='#FFF3CD', alpha=0.5, edgecolor='none')
ax.add_patch(caution_zone)

# Axes
ax.plot([6.5, 11.5], [8.5, 8.5], 'k-', linewidth=1)
ax.plot([6.5, 6.5], [8.5, 10], 'k-', linewidth=1)

# k = 2p line
ax.plot([6.5, 11.5], [8.5, 10], 'r--', linewidth=2, label=r'$k = 2p$')
ax.text(10.5, 9.6, r'$k = 2p$', fontsize=8, color='#E63946', fontweight='bold')

# Labels
ax.text(9, 8.35, r'Number of studies ($k$)', ha='center', fontsize=8)
ax.text(6.3, 9.25, r'$p$', fontsize=8, rotation=90, va='center')
ax.text(6.2, 8.8, 'Out-', fontsize=7, rotation=90, va='center')
ax.text(6.2, 8.6, 'comes', fontsize=7, rotation=90, va='center')

# Zone labels
ax.text(9.5, 9.5, 'Safe: k ≥ 2p', fontsize=7, ha='center', color='#06A77D', fontweight='bold')
ax.text(7.5, 9.5, 'Caution: k < 2p', fontsize=7, ha='center', color='#F77F00', fontweight='bold')

# Tick marks
for k in [10, 20, 30]:
    x = 6.5 + (k/30) * 5
    ax.plot([x, x], [8.5, 8.45], 'k-', linewidth=1)
    ax.text(x, 8.3, str(k), ha='center', fontsize=7)

for p in [2, 5, 10]:
    y = 8.5 + (p/15) * 1.5
    ax.plot([6.5, 6.45], [y, y], 'k-', linewidth=1)
    ax.text(6.35, y, str(p), ha='right', fontsize=7, va='center')

# Examples box
examples_box = FancyBboxPatch((6.5, 7.5), 5, 0.8, boxstyle="round,pad=0.08",
                             edgecolor='#2E86AB', facecolor='#E0F2F7', linewidth=1.5)
ax.add_patch(examples_box)
ax.text(6.7, 8.15, 'Examples:', fontsize=8, fontweight='bold')
ax.text(6.9, 7.95, r'• $p=2$ outcomes → need $k \geq 4$ studies', fontsize=7)
ax.text(6.9, 7.75, r'• $p=5$ outcomes → need $k \geq 10$ studies', fontsize=7)
ax.text(6.9, 7.55, r'• If $k < 2p$: use simpler variance structures', fontsize=7, style='italic')

# ============ PANEL C: Estimation Methods Comparison ============
ax.text(3, 6.5, 'C. Estimation Method Selection', fontsize=11, fontweight='bold')

# REML
reml_box = FancyBboxPatch((0.3, 5.5), 2.5, 0.8, boxstyle="round,pad=0.08",
                         edgecolor='#2E86AB', facecolor='#E0F2F7', linewidth=1.5)
ax.add_patch(reml_box)
ax.text(1.55, 6.15, 'REML', ha='center', fontsize=9, fontweight='bold')
ax.text(0.5, 5.9, '✓ Less biased for τ²', fontsize=7)
ax.text(0.5, 5.7, r'✓ Recommended for $k < 10$', fontsize=7)
ax.text(0.5, 5.55, 'Fast, stable', fontsize=7, style='italic')

# ML
ml_box = FancyBboxPatch((3.0, 5.5), 2.5, 0.8, boxstyle="round,pad=0.08",
                       edgecolor='#457B9D', facecolor='#F0F8FF', linewidth=1.5)
ax.add_patch(ml_box)
ax.text(4.25, 6.15, 'ML', ha='center', fontsize=9, fontweight='bold')
ax.text(3.2, 5.9, '✓ Model comparison', fontsize=7)
ax.text(3.2, 5.7, '✓ Likelihood ratio tests', fontsize=7)
ax.text(3.2, 5.55, r'Biased for small $k$', fontsize=7, style='italic')

# Bayesian
bayes_box = FancyBboxPatch((0.3, 4.5), 2.5, 0.8, boxstyle="round,pad=0.08",
                          edgecolor='#A23B72', facecolor='#F9E6F2', linewidth=1.5)
ax.add_patch(bayes_box)
ax.text(1.55, 5.15, 'Bayesian (MCMC)', ha='center', fontsize=9, fontweight='bold')
ax.text(0.5, 4.9, '✓ Full posteriors', fontsize=7)
ax.text(0.5, 4.7, '✓ Treatment rankings', fontsize=7)
ax.text(0.5, 4.55, 'Requires prior specification', fontsize=7, style='italic')

# Multiple Imputation
mi_box = FancyBboxPatch((3.0, 4.5), 2.5, 0.8, boxstyle="round,pad=0.08",
                       edgecolor='#06A77D', facecolor='#D4F4DD', linewidth=1.5)
ax.add_patch(mi_box)
ax.text(4.25, 5.15, 'Multiple Imputation', ha='center', fontsize=9, fontweight='bold')
ax.text(3.2, 4.9, '✓ Missing data (MAR)', fontsize=7)
ax.text(3.2, 4.7, r'✓ Use $M = 20\text{-}50$', fontsize=7)
ax.text(3.2, 4.55, 'Sensitivity to assumptions', fontsize=7, style='italic')

# ============ PANEL D: Critical Assumptions Checklist ============
ax.text(9, 6.5, 'D. Assumptions Checklist', fontsize=11, fontweight='bold')

assumptions = [
    ('1. Multivariate normality', 'Check effect distributions', '#2E86AB'),
    ('2. Within-study covariances known', 'Sensitivity analysis essential', '#E63946'),
    ('3. Study exchangeability', 'Random-effects assumption', '#457B9D'),
    (r'4. Correct Ψ structure', 'Consider simpler if unstable', '#A23B72'),
    ('5. MAR for missing data', 'Pattern mixture for sensitivity', '#06A77D')
]

y_start = 6.1
for i, (assumption, note, color) in enumerate(assumptions):
    y = y_start - i * 0.35

    # Checkbox
    check_box = Rectangle((6.5, y-0.05), 0.15, 0.15, edgecolor=color, facecolor='white', linewidth=1.5)
    ax.add_patch(check_box)

    # Assumption text
    ax.text(6.75, y+0.03, assumption, fontsize=8, fontweight='bold', va='center')

    # Note
    ax.text(6.75, y-0.12, note, fontsize=7, style='italic', va='center', color='#666')

# ============ PANEL E: Practical Decision Tree ============
ax.text(3, 3.9, 'E. Quick Decision Guide', fontsize=11, fontweight='bold')

# Decision flowchart
y = 3.5
# Q1
q1_box = FancyBboxPatch((1.0, y-0.15), 4, 0.4, boxstyle="round,pad=0.05",
                       edgecolor='black', facecolor='#E8E8E8', linewidth=1.5)
ax.add_patch(q1_box)
ax.text(3, y, r'Outcomes correlated?', ha='center', fontsize=8, fontweight='bold')

# Yes arrow
arrow_yes1 = FancyArrowPatch((3, y-0.15), (3, y-0.45),
                            arrowstyle='->', mutation_scale=15, linewidth=1.5, color='green')
ax.add_patch(arrow_yes1)
ax.text(3.2, y-0.3, 'Yes', fontsize=7, color='green')

# No arrow
arrow_no1 = FancyArrowPatch((5, y), (5.5, y),
                           arrowstyle='->', mutation_scale=15, linewidth=1.5, color='red')
ax.add_patch(arrow_no1)
ax.text(5.3, y+0.15, 'No', fontsize=7, color='red')

# No outcome
no_box = FancyBboxPatch((5.5, y-0.15), 2.2, 0.4, boxstyle="round,pad=0.05",
                       edgecolor='#E63946', facecolor='#FFE5E7', linewidth=1.5)
ax.add_patch(no_box)
ax.text(6.6, y, 'Univariate MA', ha='center', fontsize=8, fontweight='bold')

# Q2
y = 2.5
q2_box = FancyBboxPatch((1.0, y-0.15), 4, 0.4, boxstyle="round,pad=0.05",
                       edgecolor='black', facecolor='#E8E8E8', linewidth=1.5)
ax.add_patch(q2_box)
ax.text(3, y, r'$k \geq 2p$?', ha='center', fontsize=8, fontweight='bold')

# Yes arrow
arrow_yes2 = FancyArrowPatch((3, y-0.15), (3, y-0.45),
                            arrowstyle='->', mutation_scale=15, linewidth=1.5, color='green')
ax.add_patch(arrow_yes2)
ax.text(3.2, y-0.3, 'Yes', fontsize=7, color='green')

# No arrow
arrow_no2 = FancyArrowPatch((5, y), (5.5, y),
                           arrowstyle='->', mutation_scale=15, linewidth=1.5, color='orange')
ax.add_patch(arrow_no2)
ax.text(5.3, y+0.15, 'No', fontsize=7, color='orange')

# No outcome
small_box = FancyBboxPatch((5.5, y-0.15), 2.2, 0.4, boxstyle="round,pad=0.05",
                          edgecolor='#F77F00', facecolor='#FFF3CD', linewidth=1.5)
ax.add_patch(small_box)
ax.text(6.6, y, 'Simpler structure', ha='center', fontsize=8, fontweight='bold')

# Q3
y = 1.5
q3_box = FancyBboxPatch((1.0, y-0.15), 4, 0.4, boxstyle="round,pad=0.05",
                       edgecolor='black', facecolor='#E8E8E8', linewidth=1.5)
ax.add_patch(q3_box)
ax.text(3, y, 'Within-study ρ known?', ha='center', fontsize=8, fontweight='bold')

# Yes arrow
arrow_yes3 = FancyArrowPatch((3, y-0.15), (3, y-0.45),
                            arrowstyle='->', mutation_scale=15, linewidth=1.5, color='green')
ax.add_patch(arrow_yes3)
ax.text(3.2, y-0.3, 'Yes', fontsize=7, color='green')

# No arrow
arrow_no3 = FancyArrowPatch((5, y), (5.5, y),
                           arrowstyle='->', mutation_scale=15, linewidth=1.5, color='orange')
ax.add_patch(arrow_no3)
ax.text(5.3, y+0.15, 'No', fontsize=7, color='orange')

# No outcome
sens_box = FancyBboxPatch((5.5, y-0.15), 2.2, 0.4, boxstyle="round,pad=0.05",
                         edgecolor='#F77F00', facecolor='#FFF3CD', linewidth=1.5)
ax.add_patch(sens_box)
ax.text(6.6, y, 'Sensitivity analysis', ha='center', fontsize=8, fontweight='bold')

# Final outcome
y = 0.5
final_box = FancyBboxPatch((1.0, y-0.15), 4, 0.4, boxstyle="round,pad=0.05",
                          edgecolor='#06A77D', facecolor='#D4F4DD', linewidth=2)
ax.add_patch(final_box)
ax.text(3, y, 'Proceed with MVMA', ha='center', fontsize=9, fontweight='bold', color='#06A77D')

# Footer
ax.text(6, 0.05, 'Figure 2. Decision framework for MVMA application (A), sample size requirements showing k ≥ 2p rule (B),\n' +
        'estimation method comparison (C), critical assumptions checklist (D), and quick decision guide (E).\n' +
        'MVMA requires adequate sample size, correlated outcomes, and careful attention to assumptions.',
        ha='center', fontsize=7.5, style='italic', multialignment='center')

plt.tight_layout()
plt.savefig('/home/user/idea9/synthesis_figures/figure2_synthesis.png', dpi=300, bbox_inches='tight')
plt.savefig('/home/user/idea9/synthesis_figures/figure2_synthesis.pdf', bbox_inches='tight')
print("Figure 2 (Synthesis) saved successfully!")
plt.close()
