from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, date
import json
import pymysql
import os
pymysql.install_as_MySQLdb()

app = Flask(__name__)
CORS(app)

# ✅ Reads from Railway environment variable
db_url = os.environ.get('DATABASE_URL', '')
app.config['SQLALCHEMY_DATABASE_URI'] = db_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'moneymate_secret'

db = SQLAlchemy(app)


# ─────────────────────────────────────────
# MODELS
# ─────────────────────────────────────────

class User(db.Model):
    __tablename__ = 'users'
    id         = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name       = db.Column(db.String(255), nullable=False)
    email      = db.Column(db.String(255), unique=True, nullable=False)
    phone      = db.Column(db.String(50),  nullable=False)
    password   = db.Column(db.String(255), nullable=False)
    currency   = db.Column(db.String(10),  default='INR')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class ActiveSession(db.Model):
    __tablename__ = 'active_sessions'
    id       = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email    = db.Column(db.String(255), nullable=False)
    login_at = db.Column(db.DateTime, default=datetime.utcnow)

class Transaction(db.Model):
    __tablename__ = 'transactions'
    id         = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id    = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    type       = db.Column(db.String(10), nullable=False)
    amount     = db.Column(db.Numeric(12, 2), nullable=False)
    category   = db.Column(db.String(100), nullable=False)
    note       = db.Column(db.String(500), nullable=True)
    icon       = db.Column(db.String(50),  nullable=True)
    color      = db.Column(db.String(20),  nullable=True)
    txn_date   = db.Column(db.Date, nullable=False, default=date.today)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Budget(db.Model):
    __tablename__ = 'budgets'
    id         = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id    = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    category   = db.Column(db.String(100), nullable=False)
    icon       = db.Column(db.String(50),  nullable=True)
    color      = db.Column(db.String(20),  nullable=True)
    amount     = db.Column(db.Numeric(12, 2), nullable=False)
    month      = db.Column(db.String(7),   nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class SavingsGoal(db.Model):
    __tablename__ = 'savings_goals'
    id         = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id    = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    label      = db.Column(db.String(255), nullable=False)
    icon       = db.Column(db.String(50),  nullable=True)
    color      = db.Column(db.String(20),  nullable=True)
    target     = db.Column(db.Numeric(12, 2), nullable=False)
    saved      = db.Column(db.Numeric(12, 2), default=0.00)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class SavingsContribution(db.Model):
    __tablename__ = 'savings_contributions'
    id             = db.Column(db.Integer, primary_key=True, autoincrement=True)
    goal_id        = db.Column(db.Integer, db.ForeignKey('savings_goals.id'), nullable=False)
    user_id        = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    amount         = db.Column(db.Numeric(12, 2), nullable=False)
    note           = db.Column(db.String(255), nullable=True)
    contributed_at = db.Column(db.DateTime, default=datetime.utcnow)

class Emi(db.Model):
    __tablename__ = 'emis'
    id           = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id      = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    label        = db.Column(db.String(255), nullable=False)
    icon         = db.Column(db.String(50),  nullable=True)
    color        = db.Column(db.String(20),  nullable=True)
    bank         = db.Column(db.String(100), nullable=True)
    emi_amount   = db.Column(db.Numeric(12, 2), nullable=False)
    total_months = db.Column(db.Integer, nullable=False)
    paid_months  = db.Column(db.Integer, default=0)
    due_day      = db.Column(db.Integer, nullable=False)
    status       = db.Column(db.String(10), default='active')
    created_at   = db.Column(db.DateTime, default=datetime.utcnow)

class Bill(db.Model):
    __tablename__ = 'bills'
    id         = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id    = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    label      = db.Column(db.String(255), nullable=False)
    icon       = db.Column(db.String(50),  nullable=True)
    color      = db.Column(db.String(20),  nullable=True)
    amount     = db.Column(db.Numeric(12, 2), nullable=False)
    due_day    = db.Column(db.Integer, nullable=False)
    is_paid    = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Goal(db.Model):
    __tablename__ = 'goals'
    id         = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id    = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    label      = db.Column(db.String(255), nullable=False)
    icon       = db.Column(db.String(50),  nullable=True)
    color      = db.Column(db.String(20),  nullable=True)
    progress   = db.Column(db.Numeric(5, 2), default=0.00)
    milestones = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# ─────────────────────────────────────────
# AUTH
# ─────────────────────────────────────────

@app.route('/signup', methods=['POST'])
def signup():
    try:
        data = request.get_json()
        required = ['name', 'email', 'phone', 'password', 'confirm_password']
        if not data or not all(k in data for k in required):
            return jsonify({'error': 'Missing required fields'}), 400
        if data['password'] != data['confirm_password']:
            return jsonify({'error': 'Passwords do not match'}), 400
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'error': 'Email already registered'}), 409
        new_user = User(
            name=data['name'], email=data['email'], phone=data['phone'],
            password=generate_password_hash(data['password']),
            currency=data.get('currency', 'INR')
        )
        db.session.add(new_user)
        db.session.commit()
        return jsonify({'message': 'User registered successfully'}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@app.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        if not data or 'email' not in data or 'password' not in data:
            return jsonify({'error': 'Email and password required'}), 400
        user = User.query.filter_by(email=data['email']).first()
        if not user or not check_password_hash(user.password, data['password']):
            return jsonify({'error': 'Invalid credentials'}), 401
        session = ActiveSession(email=user.email)
        db.session.add(session)
        db.session.commit()
        return jsonify({'message': 'Login successful', 'user': {
            'id': user.id, 'name': user.name, 'email': user.email,
            'phone': user.phone, 'currency': user.currency
        }}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@app.route('/get_current_user', methods=['GET'])
def get_current_user():
    try:
        last = ActiveSession.query.order_by(ActiveSession.id.desc()).first()
        if not last:
            return jsonify({'error': 'No active user found'}), 404
        user = User.query.filter_by(email=last.email).first()
        if not user:
            return jsonify({'error': 'User not found'}), 404
        return jsonify({
            'id': user.id, 'name': user.name, 'email': user.email,
            'phone': user.phone, 'currency': user.currency
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/logout', methods=['POST'])
def logout():
    try:
        data  = request.get_json()
        email = data.get('email') if data else None
        if not email:
            return jsonify({'error': 'Email required'}), 400
        ActiveSession.query.filter_by(email=email).delete()
        db.session.commit()
        return jsonify({'message': 'Logged out successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# ─────────────────────────────────────────
# PROFILE
# ─────────────────────────────────────────

@app.route('/profile/<int:user_id>', methods=['GET'])
def get_profile(user_id):
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        return jsonify({
            'id': user.id, 'name': user.name, 'email': user.email,
            'phone': user.phone, 'currency': user.currency,
            'created_at': user.created_at.strftime('%d %b %Y')
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/profile/<int:user_id>', methods=['PUT'])
def update_profile(user_id):
    try:
        data = request.get_json()
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        user.name     = data.get('name',     user.name)
        user.phone    = data.get('phone',    user.phone)
        user.currency = data.get('currency', user.currency)
        db.session.commit()
        return jsonify({'message': 'Profile updated'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# ─────────────────────────────────────────
# TRANSACTIONS
# ─────────────────────────────────────────

@app.route('/transactions/<int:user_id>', methods=['GET'])
def get_transactions(user_id):
    try:
        txn_type = request.args.get('type')
        category = request.args.get('category')
        month    = request.args.get('month')
        limit    = int(request.args.get('limit', 50))
        query    = Transaction.query.filter_by(user_id=user_id)
        if txn_type:
            query = query.filter_by(type=txn_type)
        if category:
            query = query.filter_by(category=category)
        if month:
            query = query.filter(db.func.date_format(Transaction.txn_date, '%Y-%m') == month)
        txns = query.order_by(Transaction.txn_date.desc(), Transaction.created_at.desc()).limit(limit).all()
        return jsonify([{
            'id': t.id, 'type': t.type, 'amount': float(t.amount),
            'category': t.category, 'note': t.note,
            'icon': t.icon, 'color': t.color,
            'txn_date': t.txn_date.strftime('%d %b %Y')
        } for t in txns]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/transactions', methods=['POST'])
def add_transaction():
    try:
        data     = request.get_json()
        required = ['user_id', 'type', 'amount', 'category']
        if not data or not all(k in data for k in required):
            return jsonify({'error': 'Missing required fields'}), 400
        if data['type'] not in ('expense', 'income'):
            return jsonify({'error': "type must be 'expense' or 'income'"}), 400
        txn_date = datetime.strptime(data['txn_date'], '%Y-%m-%d').date() \
            if data.get('txn_date') else date.today()
        txn = Transaction(
            user_id=data['user_id'], type=data['type'],
            amount=data['amount'], category=data['category'],
            note=data.get('note', ''), icon=data.get('icon', ''),
            color=data.get('color', ''), txn_date=txn_date
        )
        db.session.add(txn)
        db.session.commit()
        return jsonify({'message': 'Transaction saved', 'id': txn.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/transactions/<int:txn_id>', methods=['DELETE'])
def delete_transaction(txn_id):
    try:
        txn = Transaction.query.get(txn_id)
        if not txn:
            return jsonify({'error': 'Transaction not found'}), 404
        db.session.delete(txn)
        db.session.commit()
        return jsonify({'message': 'Transaction deleted'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/transactions/summary/<int:user_id>', methods=['GET'])
def get_summary(user_id):
    try:
        month = request.args.get('month', datetime.utcnow().strftime('%Y-%m'))
        txns  = Transaction.query.filter_by(user_id=user_id).filter(
            db.func.date_format(Transaction.txn_date, '%Y-%m') == month
        ).all()
        total_income  = sum(float(t.amount) for t in txns if t.type == 'income')
        total_expense = sum(float(t.amount) for t in txns if t.type == 'expense')
        category_map = {}
        for t in txns:
            if t.type == 'expense':
                if t.category not in category_map:
                    category_map[t.category] = {'category': t.category,
                                                 'icon': t.icon, 'color': t.color, 'total': 0.0}
                category_map[t.category]['total'] += float(t.amount)
        return jsonify({
            'month': month,
            'total_income': round(total_income, 2),
            'total_expense': round(total_expense, 2),
            'net_balance': round(total_income - total_expense, 2),
            'categories': list(category_map.values())
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/transactions/monthly_chart/<int:user_id>', methods=['GET'])
def get_monthly_chart(user_id):
    try:
        rows = db.session.execute(db.text("""
            SELECT DATE_FORMAT(txn_date, '%b') AS month,
                   DATE_FORMAT(txn_date, '%Y-%m') AS month_key,
                   SUM(amount) AS total
            FROM transactions
            WHERE user_id = :uid AND type = 'expense'
              AND txn_date >= DATE_SUB(CURDATE(), INTERVAL 6 MONTH)
            GROUP BY month_key, month
            ORDER BY month_key ASC
        """), {'uid': user_id}).fetchall()
        return jsonify([{'month': r[0], 'month_key': r[1], 'total': float(r[2])} for r in rows]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ─────────────────────────────────────────
# BUDGETS
# ─────────────────────────────────────────

@app.route('/budgets/<int:user_id>', methods=['GET'])
def get_budgets(user_id):
    try:
        month   = request.args.get('month', datetime.utcnow().strftime('%Y-%m'))
        budgets = Budget.query.filter_by(user_id=user_id, month=month).all()
        result  = []
        for b in budgets:
            spent = db.session.execute(db.text("""
                SELECT COALESCE(SUM(amount), 0)
                FROM transactions
                WHERE user_id = :uid AND type = 'expense'
                  AND category = :cat
                  AND DATE_FORMAT(txn_date, '%Y-%m') = :month
            """), {'uid': user_id, 'cat': b.category, 'month': month}).scalar()
            result.append({
                'id': b.id, 'category': b.category, 'icon': b.icon,
                'color': b.color, 'limit': float(b.amount),
                'spent': float(spent), 'month': b.month
            })
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/budgets', methods=['POST'])
def add_budget():
    try:
        data     = request.get_json()
        required = ['user_id', 'category', 'amount']
        if not data or not all(k in data for k in required):
            return jsonify({'error': 'Missing required fields'}), 400
        month    = data.get('month', datetime.utcnow().strftime('%Y-%m'))
        existing = Budget.query.filter_by(user_id=data['user_id'],
                                          category=data['category'], month=month).first()
        if existing:
            return jsonify({'error': 'Budget for this category already exists this month'}), 409
        budget = Budget(
            user_id=data['user_id'], category=data['category'],
            icon=data.get('icon', ''), color=data.get('color', ''),
            amount=data['amount'], month=month
        )
        db.session.add(budget)
        db.session.commit()
        return jsonify({'message': 'Budget added', 'id': budget.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/budgets/<int:budget_id>', methods=['PUT'])
def update_budget(budget_id):
    try:
        data   = request.get_json()
        budget = Budget.query.get(budget_id)
        if not budget:
            return jsonify({'error': 'Budget not found'}), 404
        budget.amount = data.get('amount', budget.amount)
        db.session.commit()
        return jsonify({'message': 'Budget updated'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/budgets/<int:budget_id>', methods=['DELETE'])
def delete_budget(budget_id):
    try:
        budget = Budget.query.get(budget_id)
        if not budget:
            return jsonify({'error': 'Budget not found'}), 404
        db.session.delete(budget)
        db.session.commit()
        return jsonify({'message': 'Budget deleted'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# ─────────────────────────────────────────
# SAVINGS GOALS
# ─────────────────────────────────────────

@app.route('/savings_goals/<int:user_id>', methods=['GET'])
def get_savings_goals(user_id):
    try:
        goals = SavingsGoal.query.filter_by(user_id=user_id)\
            .order_by(SavingsGoal.created_at.desc()).all()
        return jsonify([{
            'id': g.id, 'label': g.label, 'icon': g.icon, 'color': g.color,
            'target': float(g.target), 'saved': float(g.saved),
            'percent': round((float(g.saved) / float(g.target)) * 100, 1) if float(g.target) > 0 else 0,
            'updated_at': g.updated_at.strftime('%d %b %Y') if g.updated_at else None
        } for g in goals]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/savings_goals', methods=['POST'])
def add_savings_goal():
    try:
        data     = request.get_json()
        required = ['user_id', 'label', 'target']
        if not data or not all(k in data for k in required):
            return jsonify({'error': 'Missing required fields'}), 400
        goal = SavingsGoal(
            user_id=data['user_id'], label=data['label'],
            icon=data.get('icon', ''), color=data.get('color', ''),
            target=data['target'], saved=data.get('saved', 0.0)
        )
        db.session.add(goal)
        db.session.commit()
        return jsonify({'message': 'Goal created', 'id': goal.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/savings_goals/<int:goal_id>', methods=['PUT'])
def update_savings_goal(goal_id):
    try:
        data = request.get_json()
        goal = SavingsGoal.query.get(goal_id)
        if not goal:
            return jsonify({'error': 'Goal not found'}), 404
        goal.label  = data.get('label',  goal.label)
        goal.target = data.get('target', goal.target)
        db.session.commit()
        return jsonify({'message': 'Goal updated'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/savings_goals/<int:goal_id>', methods=['DELETE'])
def delete_savings_goal(goal_id):
    try:
        goal = SavingsGoal.query.get(goal_id)
        if not goal:
            return jsonify({'error': 'Goal not found'}), 404
        db.session.delete(goal)
        db.session.commit()
        return jsonify({'message': 'Goal deleted'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/savings_goals/<int:goal_id>/add_money', methods=['POST'])
def add_money_to_goal(goal_id):
    try:
        data   = request.get_json()
        amount = data.get('amount') if data else None
        if not amount or float(amount) <= 0:
            return jsonify({'error': 'Valid amount required'}), 400
        goal = SavingsGoal.query.get(goal_id)
        if not goal:
            return jsonify({'error': 'Goal not found'}), 404
        goal.saved = float(goal.saved) + float(amount)
        contribution = SavingsContribution(
            goal_id=goal_id, user_id=goal.user_id,
            amount=amount, note=data.get('note', '')
        )
        db.session.add(contribution)
        db.session.commit()
        return jsonify({
            'message': 'Amount added',
            'saved': float(goal.saved),
            'percent': round((float(goal.saved) / float(goal.target)) * 100, 1)
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/savings_goals/<int:goal_id>/contributions', methods=['GET'])
def get_contributions(goal_id):
    try:
        contribs = SavingsContribution.query.filter_by(goal_id=goal_id)\
            .order_by(SavingsContribution.contributed_at.desc()).all()
        return jsonify([{
            'id': c.id, 'amount': float(c.amount), 'note': c.note,
            'contributed_at': c.contributed_at.strftime('%d %b %Y')
        } for c in contribs]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ─────────────────────────────────────────
# EMI TRACKER
# ─────────────────────────────────────────

@app.route('/emis/<int:user_id>', methods=['GET'])
def get_emis(user_id):
    try:
        status = request.args.get('status', 'active')
        emis   = Emi.query.filter_by(user_id=user_id, status=status)\
            .order_by(Emi.due_day.asc()).all()
        today  = date.today()
        result = []
        for e in emis:
            try:
                next_due = date(today.year, today.month, e.due_day)
            except ValueError:
                next_due = date(today.year, today.month, 28)
            if next_due < today:
                m = today.month + 1 if today.month < 12 else 1
                y = today.year if today.month < 12 else today.year + 1
                try:
                    next_due = date(y, m, e.due_day)
                except ValueError:
                    next_due = date(y, m, 28)
            days_left   = (next_due - today).days
            outstanding = float(e.emi_amount) * (e.total_months - e.paid_months)
            result.append({
                'id': e.id, 'label': e.label, 'icon': e.icon, 'color': e.color,
                'bank': e.bank, 'emi_amount': float(e.emi_amount),
                'total_months': e.total_months, 'paid_months': e.paid_months,
                'remaining_months': e.total_months - e.paid_months,
                'due_day': e.due_day, 'days_left': days_left,
                'outstanding': round(outstanding, 2),
                'percent_paid': round((e.paid_months / e.total_months) * 100, 1),
                'status': e.status
            })
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/emis', methods=['POST'])
def add_emi():
    try:
        data     = request.get_json()
        required = ['user_id', 'label', 'emi_amount', 'total_months', 'due_day']
        if not data or not all(k in data for k in required):
            return jsonify({'error': 'Missing required fields'}), 400
        emi = Emi(
            user_id=data['user_id'], label=data['label'],
            icon=data.get('icon', ''), color=data.get('color', ''),
            bank=data.get('bank', ''), emi_amount=data['emi_amount'],
            total_months=data['total_months'],
            paid_months=data.get('paid_months', 0),
            due_day=data['due_day']
        )
        db.session.add(emi)
        db.session.commit()
        return jsonify({'message': 'EMI added', 'id': emi.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/emis/<int:emi_id>/pay', methods=['POST'])
def mark_emi_paid(emi_id):
    try:
        emi = Emi.query.get(emi_id)
        if not emi:
            return jsonify({'error': 'EMI not found'}), 404
        emi.paid_months += 1
        if emi.paid_months >= emi.total_months:
            emi.status = 'closed'
        db.session.commit()
        return jsonify({
            'message': 'EMI marked as paid',
            'paid_months': emi.paid_months,
            'status': emi.status
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/emis/<int:emi_id>', methods=['DELETE'])
def delete_emi(emi_id):
    try:
        emi = Emi.query.get(emi_id)
        if not emi:
            return jsonify({'error': 'EMI not found'}), 404
        db.session.delete(emi)
        db.session.commit()
        return jsonify({'message': 'EMI deleted'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# ─────────────────────────────────────────
# BILLS
# ─────────────────────────────────────────

@app.route('/bills/<int:user_id>', methods=['GET'])
def get_bills(user_id):
    try:
        is_paid = request.args.get('is_paid')
        query   = Bill.query.filter_by(user_id=user_id)
        if is_paid is not None:
            query = query.filter_by(is_paid=bool(int(is_paid)))
        bills  = query.order_by(Bill.due_day.asc()).all()
        today  = date.today()
        result = []
        for b in bills:
            try:
                due_date = date(today.year, today.month, b.due_day)
            except ValueError:
                due_date = date(today.year, today.month, 28)
            days_left = (due_date - today).days
            result.append({
                'id': b.id, 'label': b.label, 'icon': b.icon, 'color': b.color,
                'amount': float(b.amount), 'due_day': b.due_day,
                'days_left': days_left, 'is_paid': b.is_paid
            })
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/bills', methods=['POST'])
def add_bill():
    try:
        data     = request.get_json()
        required = ['user_id', 'label', 'amount', 'due_day']
        if not data or not all(k in data for k in required):
            return jsonify({'error': 'Missing required fields'}), 400
        bill = Bill(
            user_id=data['user_id'], label=data['label'],
            icon=data.get('icon', ''), color=data.get('color', ''),
            amount=data['amount'], due_day=data['due_day']
        )
        db.session.add(bill)
        db.session.commit()
        return jsonify({'message': 'Bill added', 'id': bill.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/bills/<int:bill_id>/pay', methods=['POST'])
def mark_bill_paid(bill_id):
    try:
        bill = Bill.query.get(bill_id)
        if not bill:
            return jsonify({'error': 'Bill not found'}), 404
        bill.is_paid = True
        db.session.commit()
        return jsonify({'message': 'Bill marked as paid'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/bills/<int:bill_id>/unpay', methods=['POST'])
def mark_bill_unpaid(bill_id):
    try:
        bill = Bill.query.get(bill_id)
        if not bill:
            return jsonify({'error': 'Bill not found'}), 404
        bill.is_paid = False
        db.session.commit()
        return jsonify({'message': 'Bill marked as unpaid'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/bills/<int:bill_id>', methods=['DELETE'])
def delete_bill(bill_id):
    try:
        bill = Bill.query.get(bill_id)
        if not bill:
            return jsonify({'error': 'Bill not found'}), 404
        db.session.delete(bill)
        db.session.commit()
        return jsonify({'message': 'Bill deleted'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# ─────────────────────────────────────────
# GOALS (MILESTONE TRACKER)
# ─────────────────────────────────────────

@app.route('/goals/<int:user_id>', methods=['GET'])
def get_goals(user_id):
    try:
        goals = Goal.query.filter_by(user_id=user_id)\
            .order_by(Goal.created_at.desc()).all()
        return jsonify([{
            'id': g.id, 'label': g.label, 'icon': g.icon, 'color': g.color,
            'progress': float(g.progress),
            'milestones': json.loads(g.milestones) if g.milestones else [],
            'updated_at': g.updated_at.strftime('%d %b %Y') if g.updated_at else None
        } for g in goals]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/goals', methods=['POST'])
def add_goal():
    try:
        data     = request.get_json()
        required = ['user_id', 'label']
        if not data or not all(k in data for k in required):
            return jsonify({'error': 'Missing required fields'}), 400
        goal = Goal(
            user_id=data['user_id'], label=data['label'],
            icon=data.get('icon', ''), color=data.get('color', ''),
            progress=data.get('progress', 0.0),
            milestones=json.dumps(data.get('milestones', []))
        )
        db.session.add(goal)
        db.session.commit()
        return jsonify({'message': 'Goal added', 'id': goal.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/goals/<int:goal_id>', methods=['PUT'])
def update_goal(goal_id):
    try:
        data = request.get_json()
        goal = Goal.query.get(goal_id)
        if not goal:
            return jsonify({'error': 'Goal not found'}), 404
        goal.label    = data.get('label',    goal.label)
        goal.progress = data.get('progress', goal.progress)
        if 'milestones' in data:
            goal.milestones = json.dumps(data['milestones'])
        db.session.commit()
        return jsonify({'message': 'Goal updated'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/goals/<int:goal_id>', methods=['DELETE'])
def delete_goal(goal_id):
    try:
        goal = Goal.query.get(goal_id)
        if not goal:
            return jsonify({'error': 'Goal not found'}), 404
        db.session.delete(goal)
        db.session.commit()
        return jsonify({'message': 'Goal deleted'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# ─────────────────────────────────────────
# DASHBOARD
# ─────────────────────────────────────────

@app.route('/dashboard/<int:user_id>', methods=['GET'])
def get_dashboard(user_id):
    try:
        month = request.args.get('month', datetime.utcnow().strftime('%Y-%m'))
        today = date.today()

        txns          = Transaction.query.filter_by(user_id=user_id).filter(
            db.func.date_format(Transaction.txn_date, '%Y-%m') == month).all()
        total_income  = sum(float(t.amount) for t in txns if t.type == 'income')
        total_expense = sum(float(t.amount) for t in txns if t.type == 'expense')

        all_txns    = Transaction.query.filter_by(user_id=user_id).all()
        all_income  = sum(float(t.amount) for t in all_txns if t.type == 'income')
        all_expense = sum(float(t.amount) for t in all_txns if t.type == 'expense')

        recent = Transaction.query.filter_by(user_id=user_id)\
            .order_by(Transaction.txn_date.desc(), Transaction.created_at.desc())\
            .limit(4).all()

        budgets_data = []
        budgets = Budget.query.filter_by(user_id=user_id, month=month).all()
        for b in budgets:
            spent = db.session.execute(db.text("""
                SELECT COALESCE(SUM(amount), 0) FROM transactions
                WHERE user_id = :uid AND type = 'expense'
                  AND category = :cat
                  AND DATE_FORMAT(txn_date, '%Y-%m') = :month
            """), {'uid': user_id, 'cat': b.category, 'month': month}).scalar()
            budgets_data.append({
                'category': b.category, 'icon': b.icon, 'color': b.color,
                'limit': float(b.amount), 'spent': float(spent)
            })

        goals       = SavingsGoal.query.filter_by(user_id=user_id).all()
        total_saved = sum(float(g.saved) for g in goals)

        upcoming_bills = []
        for b in Bill.query.filter_by(user_id=user_id, is_paid=False).all():
            try:
                due_date = date(today.year, today.month, b.due_day)
            except ValueError:
                due_date = date(today.year, today.month, 28)
            days_left = (due_date - today).days
            if 0 <= days_left <= 7:
                upcoming_bills.append({
                    'id': b.id, 'label': b.label, 'icon': b.icon,
                    'amount': float(b.amount), 'days_left': days_left
                })

        return jsonify({
            'balance': round(all_income - all_expense, 2),
            'month_income': round(total_income, 2),
            'month_expense': round(total_expense, 2),
            'total_saved': round(total_saved, 2),
            'recent_transactions': [{
                'id': t.id, 'type': t.type, 'amount': float(t.amount),
                'category': t.category, 'note': t.note,
                'icon': t.icon, 'color': t.color,
                'txn_date': t.txn_date.strftime('%d %b %Y')
            } for t in recent],
            'budgets': budgets_data,
            'upcoming_bills': upcoming_bills
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)
