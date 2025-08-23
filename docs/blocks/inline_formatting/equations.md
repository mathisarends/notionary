# Inline Equations

Add mathematical expressions directly within text using LaTeX syntax. Inline equations render beautifully alongside regular text without breaking the flow of your content.

## Overview

Inline equations use LaTeX mathematical notation wrapped in single dollar signs. They integrate seamlessly with other inline formatting and work across all text-based blocks.

## Basic Syntax

### Simple Equations

Use single dollar signs to wrap mathematical expressions:

```markdown
The famous equation is $E = mc^2$ from Einstein.
Calculate the area using $A = \pi r^2$ for circles.
The quadratic formula: $x = \frac{-b \pm \sqrt{b^2 - 4ac}}{2a}$
```

**Result:** The famous equation is E = mc² from Einstein.

### Variables and Constants

```markdown
Set $x = 5$ and $y = 3$ to solve for $z$.
The constant $\pi \approx 3.14159$ is fundamental in geometry.
Use $\alpha$ and $\beta$ as angular measurements.
```

## Mathematical Notation

### Superscripts and Subscripts

```markdown
$x^2 + y^2 = z^2$ (Pythagorean theorem)
$H_2O$ represents water molecules
$a_1, a_2, \ldots, a_n$ for sequences
$2^{10} = 1024$ for powers of two
```

### Fractions

```markdown
Simple fraction: $\frac{1}{2}$ represents one half
Complex fraction: $\frac{a + b}{c - d}$ with variables
Nested fractions: $\frac{1}{1 + \frac{1}{x}}$ for continued fractions
```

### Roots and Radicals

```markdown
Square root: $\sqrt{16} = 4$
Cube root: $\sqrt[3]{27} = 3$
Complex root: $\sqrt{x^2 + y^2}$ for distance formula
```

### Greek Letters

```markdown
Common angles: $\alpha$, $\beta$, $\gamma$, $\theta$
Mathematical constants: $\pi$, $\phi$, $\tau$
Statistical notation: $\mu$ (mean), $\sigma$ (standard deviation)
Physics: $\lambda$ (wavelength), $\omega$ (frequency)
```

## Advanced Expressions

### Summations and Products

```markdown
Sum notation: $\sum_{i=1}^{n} i = \frac{n(n+1)}{2}$
Product notation: $\prod_{i=1}^{n} i = n!$ (factorial)
Infinite series: $\sum_{n=0}^{\infty} \frac{x^n}{n!} = e^x$
```

### Integrals and Derivatives

```markdown
Basic integral: $\int x dx = \frac{x^2}{2} + C$
Definite integral: $\int_0^1 x^2 dx = \frac{1}{3}$
Derivative: $\frac{d}{dx}(x^2) = 2x$
Partial derivative: $\frac{\partial f}{\partial x}$
```

### Limits and Sequences

```markdown
Basic limit: $\lim_{x \to 0} \frac{\sin x}{x} = 1$
Infinite limit: $\lim_{n \to \infty} \frac{1}{n} = 0$
Sequence: $a_n = \frac{1}{n^2}$ converges to $0$
```

### Matrices and Vectors

```markdown
Vector notation: $\vec{v} = (x, y, z)$
Matrix: $\begin{pmatrix} a & b \\ c & d \end{pmatrix}$
Determinant: $\det(A) = ad - bc$ for 2×2 matrices
```

## Combining with Other Formatting

### Equations with Rich Text

Combine equations with other inline formatting:

```markdown
**Important:** The relationship $F = ma$ shows **force equals mass times acceleration**.
_Note:_ Use $\Delta t$ to represent _time intervals_ in calculations.
The result is $x = 42$ - see `calculation.py` for implementation.
```

### Equations with Colors

Add emphasis using color formatting:

```markdown
(red:$\mathbf{Warning:}$ Division by zero in $\frac{1}{x}$ when $x = 0$)
(green_background:$\checkmark$ Solution: $x = \frac{-b}{2a}$ is correct)
(blue:For reference: $\pi \approx 3.14159$ in most calculations)
```

### Equations with Mentions

Reference related content:

```markdown
See @page[Calculus Notes] for the derivation of $\frac{d}{dx}(\sin x) = \cos x$.
Ask @user[Math Professor] about the proof of $e^{i\pi} + 1 = 0$.
Check @database[Formula Repository] for more equations like $\int e^x dx = e^x + C$.
```

## Practical Examples

### Physics

```markdown
**Classical Mechanics:**

- Force: $F = ma$ (Newton's second law)
- Energy: $E = \frac{1}{2}mv^2$ (kinetic energy)
- Momentum: $p = mv$ (conservation principle)

**Electromagnetism:**

- Coulomb's law: $F = k\frac{q_1 q_2}{r^2}$
- Ohm's law: $V = IR$ (voltage, current, resistance)
```

### Statistics

```markdown
**Descriptive Statistics:**

- Mean: $\bar{x} = \frac{1}{n}\sum_{i=1}^{n} x_i$
- Variance: $\sigma^2 = \frac{1}{n}\sum_{i=1}^{n} (x_i - \bar{x})^2$
- Standard deviation: $\sigma = \sqrt{\sigma^2}$

**Probability:**

- Normal distribution: $f(x) = \frac{1}{\sigma\sqrt{2\pi}} e^{-\frac{(x-\mu)^2}{2\sigma^2}}$
```

### Computer Science

```markdown
**Algorithm Analysis:**

- Time complexity: $O(n \log n)$ for efficient sorting
- Space complexity: $O(1)$ for constant space
- Recurrence: $T(n) = 2T(n/2) + O(n)$ for divide-and-conquer

**Information Theory:**

- Entropy: $H(X) = -\sum_{i} p_i \log_2 p_i$
- Shannon's theorem: $C = B \log_2(1 + \frac{S}{N})$
```

## Best Practices

### Readability

- Use equations to clarify relationships, not to show off
- Provide context before and after complex equations
- Define variables when first introduced

### Formatting Guidelines

```markdown
✅ Good: Clear and contextual
The gravitational force $F = G\frac{m_1 m_2}{r^2}$ decreases with distance.

❌ Avoid: Equations without context
Just use $F = G\frac{m_1 m_2}{r^2}$ here.
```

### Variable Naming

- Use standard conventions (e.g., $x$, $y$ for coordinates)
- Be consistent with notation throughout your content
- Define custom variables clearly

## Troubleshooting

### Common Issues

**Missing Dollar Signs:**

```markdown
❌ E = mc^2 (not rendered as equation)
✅ $E = mc^2$ (properly formatted)
```

**Unmatched Braces:**

```markdown
❌ $\frac{a + b}{c$ (missing closing brace)
✅ $\frac{a + b}{c}$ (properly closed)
```

**Special Characters:**

```markdown
❌ $x & y$ (& has special meaning)
✅ $x \text{ and } y$ (use \text for words)
```

## Related Features

- **[Rich Text Formatting](rich_text.md)** - Basic text styling
- **[Colors & Highlights](colors_and_highlights.md)** - Visual emphasis
- **[Mentions](mentions.md)** - Reference users, pages, and databases
- **[Equation Blocks](../equation.md)** - Display-style mathematical expressions
