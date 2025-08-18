# Equation Blocks

Equation blocks render mathematical expressions using LaTeX syntax. Perfect for scientific documentation, educational content, and technical specifications.

## Basic Syntax

```markdown
[equation](E = mc^2)
[equation]("f(x) = ax^2 + bx + c")
```

## Simple Equations

### Basic Mathematical Operations

```markdown
[equation](x + y = z)
[equation](a - b = c)
[equation](x \cdot y = z)
[equation](a / b = c)
[equation](x^2 + y^2 = z^2)
```

### Common Formulas

```markdown
# Physics

[equation](E = mc^2)
[equation](F = ma)
[equation](v = v_0 + at)

# Mathematics

[equation](x = \frac{-b \pm \sqrt{b^2 - 4ac}}{2a})
[equation](A = \pi r^2)
[equation](c^2 = a^2 + b^2)

# Statistics

[equation](\mu = \frac{1}{n} \sum*{i=1}^{n} x_i)
[equation](\sigma^2 = \frac{1}{n} \sum*{i=1}^{n} (x_i - \mu)^2)
```

## Complex Equations

### Fractions and Roots

```markdown
# Fractions

[equation]("\frac{a}{b} + \frac{c}{d} = \frac{ad + bc}{bd}")

# Square roots

[equation]("\sqrt{x^2 + y^2}")

# Nth roots

[equation]("\sqrt[n]{x}")

# Complex fractions

[equation]("\frac{\frac{a}{b}}{\frac{c}{d}} = \frac{a \cdot d}{b \cdot c}")
```

### Summations and Integrals

```markdown
# Summation notation

[equation]("\sum*{i=1}^{n} x_i")
[equation]("\sum*{k=0}^{\infty} \frac{x^k}{k!} = e^x")

# Product notation

[equation]("\prod\_{i=1}^{n} x_i")

# Integrals

[equation]("\int*{a}^{b} f(x) dx")
[equation]("\int*{-\infty}^{\infty} e^{-x^2} dx = \sqrt{\pi}")

# Partial derivatives

[equation]("\frac{\partial f}{\partial x}")
```

### Matrix Operations

```markdown
# Matrices

[equation]("\begin{pmatrix} a & b \\ c & d \end{pmatrix}")

# Matrix multiplication

[equation]("\begin{pmatrix} a & b \\ c & d \end{pmatrix} \begin{pmatrix} e \\ f \end{pmatrix} = \begin{pmatrix} ae + bf \\ ce + df \end{pmatrix}")

# Determinant

[equation]("\det(A) = ad - bc")

# Identity matrix

[equation]("I = \begin{pmatrix} 1 & 0 \\ 0 & 1 \end{pmatrix}")
```

## Quoted Syntax for Complex Expressions

When equations contain parentheses, quotes, or newlines, use quoted syntax:

```markdown
# Complex expressions with parentheses

[equation]("f(x) = \sin(x) + \cos(x)")
[equation]("P(A|B) = \frac{P(B|A) \cdot P(A)}{P(B)}")

# Multi-line expressions

[equation]("
\begin{align}
x &= a + b \\
y &= c + d \\
z &= x + y
\end{align}
")

# Expressions with special characters

[equation]("\"Hello\" = \text{greeting}")
```

## Scientific Applications

### Physics Formulas

```markdown
## Classical Mechanics

### Newton's Laws

[equation]("F = \frac{dp}{dt}")
[equation]("F = ma")

### Energy Conservation

[equation]("E = K + U")
[equation]("K = \frac{1}{2}mv^2")
[equation]("U = mgh")

### Wave Equations

[equation]("y(x,t) = A \sin(kx - \omega t + \phi)")
[equation]("v = f\lambda")

## Quantum Mechanics

### Schrödinger Equation

[equation]("i\hbar \frac{\partial \psi}{\partial t} = \hat{H} \psi")

### Uncertainty Principle

[equation]("\Delta x \Delta p \geq \frac{\hbar}{2}")

### Energy Levels

[equation]("E_n = -\frac{13.6 \text{ eV}}{n^2}")
```

### Chemistry Equations

```markdown
## Chemical Equilibrium

### Equilibrium Constant

[equation]("K_c = \frac{[C]^c[D]^d}{[A]^a[B]^b}")

### pH Calculations

[equation]("pH = -\log[H^+]")
[equation]("pOH = -\log[OH^-]")
[equation]("pH + pOH = 14")

### Reaction Rates

[equation]("rate = k[A]^m[B]^n")

### Thermodynamics

[equation]("\Delta G = \Delta H - T\Delta S")
[equation]("\Delta G = -RT \ln K")
```

### Statistics and Probability

```markdown
## Probability Distributions

### Normal Distribution

[equation]("f(x) = \frac{1}{\sigma\sqrt{2\pi}} e^{-\frac{1}{2}\left(\frac{x-\mu}{\sigma}\right)^2}")

### Binomial Distribution

[equation]("P(X = k) = \binom{n}{k} p^k (1-p)^{n-k}")

### Poisson Distribution

[equation]("P(X = k) = \frac{\lambda^k e^{-\lambda}}{k!}")

## Statistical Tests

### t-test

[equation]("t = \frac{\bar{x} - \mu_0}{s/\sqrt{n}}")

### Chi-square

[equation]("\chi^2 = \sum \frac{(O_i - E_i)^2}{E_i}")

### Correlation Coefficient

[equation]("r = \frac{\sum(x_i - \bar{x})(y_i - \bar{y})}{\sqrt{\sum(x_i - \bar{x})^2 \sum(y_i - \bar{y})^2}}")
```

## Programmatic Usage

### Creating Equations

```python
from notionary.blocks.equation import EquationMarkdownNode

# Simple equation
equation = EquationMarkdownNode(expression="E = mc^2")

# Complex equation with LaTeX
complex_eq = EquationMarkdownNode(
    expression=r"\frac{-b \pm \sqrt{b^2 - 4ac}}{2a}"
)

markdown = equation.to_markdown()
```

### Mathematical Documentation

```python
import asyncio
from notionary import NotionPage

async def create_physics_reference():
    page = await NotionPage.from_page_name("Physics Reference")

    physics_content = '''
# Physics Formula Reference

## Classical Mechanics

### Motion Equations
[equation]("v = v_0 + at")
[equation]("s = v_0 t + \\frac{1}{2}at^2")
[equation]("v^2 = v_0^2 + 2as")

### Force and Energy
[equation]("F = ma")
[equation]("W = F \\cdot d")
[equation]("P = \\frac{W}{t}")

## Electromagnetism

### Coulomb's Law
[equation]("F = k \\frac{q_1 q_2}{r^2}")

### Ohm's Law
[equation]("V = IR")

### Power
[equation]("P = VI = I^2R = \\frac{V^2}{R}")
    '''

    await page.replace_content(physics_content)

asyncio.run(create_physics_reference())
```

### Dynamic Equation Generation

```python
def create_quadratic_formula_explanation(a, b, c):
    return f'''
# Quadratic Formula Solution

## Given Equation
[equation]("{a}x^2 + {b}x + {c} = 0")

## General Solution
[equation]("x = \\frac{{-b \\pm \\sqrt{{b^2 - 4ac}}}}{{2a}}")

## Substituting Values
[equation]("x = \\frac{{-({b}) \\pm \\sqrt{{({b})^2 - 4({a})({c})}}}}{{2({a})}}")

## Discriminant
[equation]("\\Delta = b^2 - 4ac = {b**2 - 4*a*c}")
'''

# Usage
explanation = create_quadratic_formula_explanation(1, -5, 6)
await page.replace_content(explanation)
```

## Advanced LaTeX Features

### Text in Equations

```markdown
# Adding text labels

[equation]("F\_{gravity} = mg \\text{ (force of gravity)}")
[equation]("\\text{Speed} = \\frac{\\text{Distance}}{\\text{Time}}")

# Units

[equation]("v = 299,792,458 \\text{ m/s}")
[equation]("c = 3.0 \\times 10^8 \\text{ m/s}")
```

### Greek Letters

```markdown
# Common Greek letters

[equation]("\\alpha + \\beta = \\gamma")
[equation]("\\Delta x \\Delta p \\geq \\frac{\\hbar}{2}")
[equation]("\\lambda = \\frac{h}{p}")
[equation]("\\Omega = 2\\pi f")
```

### Special Symbols

```markdown
# Mathematical symbols

[equation]("x \\in \\mathbb{R}")
[equation]("A \\subset B")
[equation]("f: X \\rightarrow Y")
[equation]("\\forall x \\exists y")
[equation]("\\infty > n")
```

### Alignment and Arrays

```markdown
# Aligned equations

[equation]("
\\begin{align}
x + y &= 5 \\\\
2x - y &= 1 \\\\
\\end{align}
")

# System of equations

[equation]("
\\begin{cases}
x + y = 5 \\\\
2x - y = 1
\\end{cases}
")

# Equation arrays

[equation]("
\\begin{array}{c|c}
x & f(x) \\\\
\\hline
0 & 1 \\\\
1 & 2 \\\\
2 & 4
\\end{array}
")
```

## Common Use Cases

### Educational Content

```markdown
# Calculus Tutorial

## Derivatives

### Basic Rules

[equation]("\\frac{d}{dx}[x^n] = nx^{n-1}")]
[equation]("\\frac{d}{dx}[e^x] = e^x")]
[equation]("\\frac{d}{dx}[\\sin x] = \\cos x")]

### Chain Rule

[equation]("\\frac{d}{dx}[f(g(x))] = f'(g(x)) \\cdot g'(x)")]

### Product Rule

[equation]("\\frac{d}{dx}[f(x)g(x)] = f'(x)g(x) + f(x)g'(x)")]
```

### Research Documentation

```markdown
# Algorithm Analysis

## Time Complexity

### Big O Notation

[equation]("f(n) = O(g(n))")]

### Common Complexities

[equation]("O(1) < O(\\log n) < O(n) < O(n \\log n) < O(n^2)")]

## Space Complexity

### Recursive Algorithms

[equation]("T(n) = T(n-1) + O(1)")]
[equation]("T(n) = O(n)")]
```

### Engineering Specifications

```markdown
# Signal Processing

## Fourier Transform

[equation]("X(f) = \\int\_{-\\infty}^{\\infty} x(t) e^{-j2\\pi ft} dt")]

## Digital Filters

[equation]("H(z) = \\frac{Y(z)}{X(z)}")]

## Signal-to-Noise Ratio

[equation]("SNR = 10 \\log*{10} \\left(\\frac{P*{signal}}{P\_{noise}}\\right)")]
```

## Best Practices

### Equation Formatting

```markdown
# ✅ Good - Clear, readable expressions

[equation]("x = \\frac{-b \\pm \\sqrt{b^2 - 4ac}}{2a}")]

# ✅ Good - Proper spacing and grouping

[equation]("F = G \\frac{m_1 m_2}{r^2}")]

# ❌ Avoid - Cramped or unclear formatting

[equation](<"x=(-b+-sqrt(b^2-4ac))/(2a)">)]

# ❌ Avoid - Missing necessary grouping

[equation]("x = -b + sqrt b^2 - 4ac / 2a")]
```

### Context and Explanation

```markdown
## Proper Context Example

The quadratic formula solves equations of the form ax² + bx + c = 0:

[equation]("x = \\frac{-b \\pm \\sqrt{b^2 - 4ac}}{2a}")]

Where:

- **a, b, c** are coefficients (a ≠ 0)
- **±** indicates two possible solutions
- **Discriminant** b² - 4ac determines solution type

### Solution Types:

- **b² - 4ac > 0**: Two real solutions
- **b² - 4ac = 0**: One real solution
- **b² - 4ac < 0**: Two complex solutions
```

## Integration with Other Blocks

### Equations with Callouts

```markdown
## Important Formula

[callout](⚠️ **Remember:** This only applies when x ≠ 0 "⚠️")]

[equation]("\\lim\_{x \\to 0} \\frac{\\sin x}{x} = 1")]

[callout](💡 **Tip:** Use L'Hôpital's rule for indeterminate forms "💡")]
```

### Equations in Toggles

```markdown
+++ Derivation of Quadratic Formula
Starting with the general quadratic equation:

[equation]("ax^2 + bx + c = 0")]

Divide by a:
[equation]("x^2 + \\frac{b}{a}x + \\frac{c}{a} = 0")]

Complete the square:
[equation]("\\left(x + \\frac{b}{2a}\\right)^2 = \\frac{b^2 - 4ac}{4a^2}")]

Solve for x:
[equation]("x = \\frac{-b \\pm \\sqrt{b^2 - 4ac}}{2a}")]
+++
```

### Equations in Tables

```markdown
| Function              | Derivative             | Integral                          |
| --------------------- | ---------------------- | --------------------------------- |
| [equation]("x^n")     | [equation]("nx^{n-1}") | [equation]("\frac{x^{n+1}}{n+1}") |
| [equation]("e^x")     | [equation]("e^x")      | [equation]("e^x")                 |
| [equation]("\\sin x") | [equation]("\\cos x")  | [equation]("-\\cos x")            |
```

## Related Blocks

- **[Code](code.md)** - For computational examples
- **[Table](table.md)** - For organizing multiple equations
- **[Callout](callout.md)** - For highlighting important formulas
- **[Toggle](toggle.md)** - For collapsible derivations
