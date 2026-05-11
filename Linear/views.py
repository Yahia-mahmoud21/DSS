import io
import base64
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.optimize import linprog
from django.shortcuts import render
from django.conf import settings


class SimplexSolver:
    def __init__(self, obj, A, b, signs, mode):
        self.obj = np.array(obj, dtype=float) # [10, 20]
        self.A_orig = A # [[x, y], [x, y]]
        self.b_orig = b # [rhs, rhs]
        self.signs = signs # [">=", "<="]
        self.mode = mode.lower() # "max"
        self.n_vars = len(obj) # 2
        self.n_cons = len(b) # 2

        # Convert constraints to <= form for the simplex tableau (educational)
        self.A_simplex = [] # [[ -x, -y], [x, y ]]
        self.b_simplex = [] # [-rhs, rhs]
        for i in range(self.n_cons):
            if signs[i] == '>=':
                self.A_simplex.append([-x for x in A[i]]) 
                self.b_simplex.append(-b[i]) 
            else:
                self.A_simplex.append(A[i])
                self.b_simplex.append(b[i])

        self.A_simplex = np.array(self.A_simplex, dtype=float)
        self.b_simplex = np.array(self.b_simplex, dtype=float)

        # Build initial table
        self.cols = [f"X{i+1}" for i in range(self.n_vars)] + [f"S{i+1}" for i in range(self.n_cons)] + ["RHS"]
        self.rows = [f"S{i+1}" for i in range(self.n_cons)] + ["Z"]
        self.table = np.zeros((self.n_cons + 1, len(self.cols))) # np.zeros((4, 6))
        self.iterations = []
                # [   3                 2    ] = [[-x, -y], [x, y], [x , y]]
        self.table[:self.n_cons , :self.n_vars] = self.A_simplex
        self.table[:self.n_cons, self.n_vars:self.n_vars + self.n_cons] = np.eye(self.n_cons)
        self.table[:self.n_cons, -1] = self.b_simplex

        if self.mode == 'max':
            self.table[-1, :self.n_vars] = -self.obj
        else:
            self.table[-1, :self.n_vars] = self.obj

    def record_tableau(self, iteration):
        rows = []
        for i in range(len(self.table)):
            label = "Z" if i == len(self.table) - 1 else f"S{i+1}"
            rows.append({
                'label': label,
                'values': [round(val, 2) for val in self.table[i]]
            })
        self.iterations.append({
            'number': iteration,
            'header': self.cols,
            'rows': rows
        })

    def solve(self):
        # Educational tableau display
        self.record_tableau(0)
        while np.any(self.table[-1, :-1] < 0):
            pivot_col = np.argmin(self.table[-1, :-1]) # smaller number in z row
            ratios = [self.table[i, -1] / self.table[i, pivot_col] if self.table[i, pivot_col] > 0 else np.inf for i in range(self.n_cons)]
            pivot_row = np.argmin(ratios)
            if ratios[pivot_row] == np.inf:
                break
            pivot_val = self.table[pivot_row, pivot_col]
            self.table[pivot_row] /= pivot_val
            for r in range(len(self.table)):
                if r != pivot_row:
                    self.table[r] -= self.table[r, pivot_col] * self.table[pivot_row]
            self.record_tableau(len(self.iterations))

        # Precise calculation using scipy linprog
        c_for_scipy = self.obj if self.mode == 'min' else -self.obj
        A_ub, b_ub, A_eq, b_eq = [], [], [], []
        for i in range(self.n_cons):
            if self.signs[i] == '<=':
                A_ub.append(self.A_orig[i])
                b_ub.append(self.b_orig[i])

            elif self.signs[i] == '>=':
                A_ub.append([-x for x in self.A_orig[i]])
                b_ub.append(-self.b_orig[i])

            elif self.signs[i] == '=':
                A_eq.append(self.A_orig[i])
                b_eq.append(self.b_orig[i])

        res = linprog(
            c_for_scipy,
            A_ub=A_ub if A_ub else None,
            b_ub=b_ub if b_ub else None,
            A_eq=A_eq if A_eq else None,
            b_eq=b_eq if b_eq else None,
            method='highs'
        )

        solution_data = {
            'iterations': self.iterations,
            'final_table': self.iterations[-1] if self.iterations else None,
            'success': res.success,
            'variables': [],
            'optimal_z': None
        }

        if res.success:
            solution_data['variables'] = [round(v, 2) for v in res.x]
            solution_data['optimal_z'] = round(res.fun if self.mode == 'min' else -res.fun, 2)

        return solution_data


def solve_graphical(obj, A, b, signs, mode):
    if any(len(row) != 2 for row in A):
        raise ValueError("Graphical method requires exactly 2 variables per constraint")

    limit = max(b) * 1.5 if b else 20
    x = np.linspace(0, limit, 400)

    fig, ax = plt.subplots(figsize=(8, 8))
    feasible_region = np.ones_like(x) * limit
    bottom_boundary = np.zeros_like(x)

    for i in range(len(A)):
        if A[i][1] != 0:
            y = (b[i] - A[i][0] * x) / A[i][1]
            y_plot = np.clip(y, 0, limit)
            sign_label = signs[i] if signs[i] else '<='
            ax.plot(x, y_plot, label=f'C{i+1}: {sign_label} {b[i]}', linewidth=2)
            if signs[i] == '<=':
                feasible_region = np.minimum(feasible_region, y_plot)
            elif signs[i] == '>=':
                bottom_boundary = np.maximum(bottom_boundary, y_plot)
            elif signs[i] == '=':
                ax.plot(x, y_plot, color='black', linestyle='--', linewidth=2, label=f'C{i+1} (MUST BE ON THIS LINE)')
        else:
            val = b[i] / A[i][0]
            ax.axvline(x=val, label=f'C{i+1} Vertical', linewidth=2)

    ax.fill_between(x, bottom_boundary, feasible_region,
                    where=(feasible_region >= bottom_boundary),
                    color='#4a90d9', alpha=0.25, hatch='//', label='Feasible Region')

    ax.set_xlim(0, limit)
    ax.set_ylim(0, limit)
    ax.axhline(0, color='black', lw=2)
    ax.axvline(0, color='black', lw=2)
    ax.set_title(f"Graphical Method ({mode.capitalize()})", fontsize=14, fontweight='bold')
    ax.set_xlabel("X1", fontsize=12)
    ax.set_ylabel("X2", fontsize=12)
    ax.legend(loc='upper right')
    ax.grid(True, alpha=0.3)

    # Precise calculation using scipy linprog
    c_for_scipy = np.array(obj) if mode == 'min' else -np.array(obj)
    A_ub, b_ub, A_eq, b_eq = [], [], [], []
    for i in range(len(A)):
        if signs[i] == '<=':
            A_ub.append(A[i]); b_ub.append(b[i])
        elif signs[i] == '>=':
            A_ub.append([-x for x in A[i]]); b_ub.append(-b[i])
        elif signs[i] == '=':
            A_eq.append(A[i]); b_eq.append(b[i])

    res = linprog(
        c_for_scipy,
        A_ub=A_ub if A_ub else None,
        b_ub=b_ub if b_ub else None,
        A_eq=A_eq if A_eq else None,
        b_eq=b_eq if b_eq else None,
        method='highs'
    )

    result_text = None
    if res.success:
        ax.plot(res.x[0], res.x[1], 'ro', markersize=10, label='Optimal Point')
        ax.legend(loc='upper right')
        optimal_z = res.fun if mode == 'min' else -res.fun
        result_text = {
            'x1': round(res.x[0], 2),
            'x2': round(res.x[1], 2),
            'optimal_z': round(optimal_z, 2)
        }

    buf = io.BytesIO()
    fig.savefig(buf, format='png', dpi=120, bbox_inches='tight')
    buf.seek(0)
    img_base64 = base64.b64encode(buf.read()).decode('utf-8')
    plt.close(fig)
    return img_base64, result_text


def home(request):
    return render(request, 'Linear/home.html')


def solve_lp(request):
    if request.method == 'POST':
        nv = int(request.POST.get('num_vars'))
        nc = int(request.POST.get('num_cons'))
        obj = [float(request.POST.get(f'obj_coeff_{j}')) for j in range(nv)]
        A = []
        b = []
        signs = []
        for i in range(nc):
            row = [float(request.POST.get(f'constraint_{i}_{j}')) for j in range(nv)]
            A.append(row)
            signs.append(request.POST.get(f'sign_{i}', '<='))
            b.append(float(request.POST.get(f'rhs_{i}')))
        mode = request.POST.get('mode', 'max')
        method = request.POST.get('method')

        if method == 'graphical' and nv == 2:
            chart, result = solve_graphical(obj, A, b, signs, mode)
            return render(request, 'Linear/graphical_result.html', {
                'chart': chart,
                'result': result,
                'obj': obj,
                'A': A,
                'b': b,
                'signs': signs,
                'mode': mode
            })
        else:
            solver = SimplexSolver(obj, A, b, signs, mode)
            solution = solver.solve()
            return render(request, 'Linear/simplex_result.html', {
                'solution': solution,
                'obj': obj,
                'A': A,
                'b': b,
                'signs': signs,
                'n_vars': nv,
                'n_cons': nc,
                'mode': mode
            })
    return render(request, 'Linear/home.html')