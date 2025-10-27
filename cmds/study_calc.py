import random

cards = {
    "What does d/dx mean?": [
        "It means 'take the derivative with respect to x'.",
        "d = a small change",
        "dx = in x (the variable we are changing)",
        "Example: d/dx (x^2) = 2x"
    ],
    "What does derivative mean?": [
        "It measures how a function changes — the rate of change at a point.",
        "In plain terms: how steep is the graph at that spot?"
    ],
    "Parts of d/dx f(x)": [
        "d = small change (infinitesimal difference)",
        "dx = with respect to x (which variable we’re using)",
        "f(x) = the function being differentiated"
    ],
    "Power rule (most common rule)": [
        "If f(x) = x^n, then d/dx f(x) = n*x^(n-1).",
        "Example: Step 1: f(x) = x^3 → n = 3",
        "Step 2: Multiply by n → 3*x^(3-1)",
        "Step 3: Simplify → 3x^2"
    ],
    "Derivative of a constant": [
        "If f(x) = C (a constant), then d/dx C = 0.",
        "Example: d/dx (5) = 0."
    ],
    "Why are derivatives useful?": [
        "They tell us slope (instantaneous rate of change).",
        "Used in physics (velocity, acceleration), economics (marginal cost), biology (growth rates), etc."
    ],
    "Extra examples": [
        "d/dx (x^5) = 5x^4",
        "d/dx (2x + 3) = 2",
        "d/dx (7) = 0"
    ],
    "Practice problems": [
        "Find d/dx (3x^2 + 4x - 5).",
        "Find d/dx (7).",
        "Find d/dx (x^4 - 2x + 1)."
    ],
    "What’s the derivative of x^n?": [
        "Rule: d/dx[x^n] = n x^{n-1}",
        "Intuition: Imagine a balloon with n layers; popping one layer reduces exponent by one and force equals the layer count.",
        "Example: d/dx[x^5] = 5x^4",
        "Variables: x = independent variable; n = constant exponent"
    ],
    "How does multiplying a function by a constant c affect its derivative?": [
        "Rule: d/dx[c f(x)] = c f'(x)",
        "Intuition: Stretching a spring by c multiplies every slope by c.",
        "Example: d/dx[3 sin x] = 3 cos x",
        "Variables: c = constant; f(x) = differentiable function; x = independent variable"
    ],
    "Derivative of a sum or difference: f(x) ± g(x)?": [
        "Rule: d/dx[f ± g] = f' ± g'",
        "Intuition: Total pull is the sum or difference of individual pulls in a tug-of-war.",
        "Example: d/dx[x^2 + ln x] = 2x + 1/x",
        "Variables: f(x), g(x) = differentiable functions; x = independent variable"
    ],
    "How to differentiate u(x) × v(x)?": [
        "Rule: (u v)' = u' v + u v'",
        "Intuition: In meshed gears, one gear speeding while the other holds, plus vice versa.",
        "Example: d/dx[x^2 e^x] = 2x e^x + x^2 e^x",
        "Variables: u(x), v(x) = differentiable functions; x = independent variable"
    ],
    "How to differentiate u(x)/v(x)?": [
        "Rule: (u/v)' = (u' v - u v') / v^2",
        "Intuition: Budget cut: change in costs minus change in budget, divided by budget squared.",
        "Example: d/dx[(x^2 -1)/x] = (2x·x - (x^2-1)·1)/x^2 = 1 + 1/x^2",
        "Variables: u(x), v(x) = differentiable; v(x) ≠ 0; x = independent variable"
    ],
    "Derivative of a composition f(g(x))?": [
        "Rule: (f ∘ g)' = f'(g(x)) · g'(x)",
        "Intuition: Assembly line: stage 2’s speed at stage 1’s output rate.",
        "Example: d/dx[ sin(x^3) ] = cos(x^3) · 3x^2",
        "Variables: f = outer function; f' = first derivative; g(x) = inner function; g' = first derivative; x = independent variable"
    ],
    "What is ∫ x^n dx?": [
        "Rule: ∫ x^n dx = x^{n+1}/(n+1) + C, n ≠ -1",
        "Intuition: Time rewind: add back an exponent layer and divide to balance scaling.",
        "Example: ∫ x^4 dx = x^5/5 + C",
        "Variables: x = integration variable; n = constant exponent; C = constant of integration"
    ],
    "∫ e^x dx and ∫ a^x dx?": [
        "Rule: ∫ e^x dx = e^x + C; ∫ a^x dx = a^x / ln a + C",
        "Intuition: Exponential grows at its own rate; reverse is same shape, scaled by 1/ln a.",
        "Example: ∫ 2^x dx = 2^x / ln 2 + C",
        "Variables: x = integration variable; a = positive base ≠ 1; C = constant of integration"
    ],
    "How to pick and use u = g(x) in integration?": [
        "Rule: 1) Let u = g(x) so du = g'(x) dx, 2) Rewrite integral in u, 3) Integrate and substitute back.",
        "Intuition: Language translation: translate a phrase, solve, translate back.",
        "Example: ∫ 2x (x^2+1)^3 dx: let u=x^2+1, du=2x dx → ∫ u^3 du = u^4/4 + C = (x^2+1)^4/4 + C",
        "Variables: u = new variable; g(x) = chosen inner function; x = original variable; C = constant of integration"
    ],
    "How to integrate ∫ u dv?": [
        "Rule: ∫ u dv = u v - ∫ v du",
        "Intuition: Trade-off: differentiate part that simplifies, integrate easier part, subtract remainder.",
        "Example: ∫ x e^x dx: let u=x, dv=e^x dx → du=dx, v=e^x → x e^x - ∫ e^x dx = x e^x - e^x + C",
        "Variables: u = chosen function to differentiate; dv = chosen function to integrate; du = u' dx; v = antiderivative of dv; C = constant"
    ]
}

n = len(cards)

while True:
    key, v = random.choice(list(cards.items()))
    print(key)
    input('flip card?')
    for x in v:
        print(x)
        input('next fact?')
    input('next questions?')
