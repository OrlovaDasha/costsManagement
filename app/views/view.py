import locale

from flask import request, render_template, redirect, url_for, session
from flask_login import current_user, login_required

from app import app, db, nav
from app.models.Goods import Goods
from app.models.Purchase import Purchase
from app.models.PurchaseConsist import PurchaseConsist
from app.models.Users import Users
from app.models.UsersPurchase import UsersPurchase

nav.Bar('top', [
    nav.Item('Главная', 'index'),
    nav.Item('Добавить транзакцию', 'tr', items=[
        nav.Item('Вручную', 'purchase'),
        nav.Item('По чеку', 'image')
    ]),
    nav.Item('История', 'nested', items=[
        nav.Item('По транзакциям', 'transactions'),
        nav.Item('По категориям', 'categorise')
    ]),
])


@app.route('/', methods=['GET', 'POST'])
def index():
    locale.setlocale(locale.LC_ALL, 'ru_RU.UTF-8')
    if current_user.is_authenticated:
        user = Users.query.filter_by(id=current_user.id).first()
        purchases = []
        purchases = db.session.query(Purchase).join(UsersPurchase).filter(UsersPurchase.user_id == user.id).order_by(Purchase.purchase_date).all()

        transactions = {}
        for purchase in purchases:
            key = purchase.purchase_date
            if key not in transactions.keys():
                transactions.setdefault(key, [])
                transactions[key].append(purchase)
            else:
                transactions[key].append(purchase)

        return render_template("index.html", username=user.username, transactions = transactions)
    else:
        return redirect(url_for('login'))


@app.route('/delete_purchase/<purchase_id>')
def delete_purchase(purchase_id):
    print('delete')
    try:
        purchase = Purchase.query.filter_by(id = purchase_id).first()
        userPurchase = UsersPurchase.query.filter_by(user_id = current_user.id, purchase_id = purchase_id).first()
        consists = PurchaseConsist.query.filter_by(purchase_id = userPurchase.id).all()
        for consist in consists:
            good = Goods.query.filter_by(id = consist.good_id).first()
            db.session.delete(consist)
            db.session.commit()
            db.session.delete(good)
            db.session.commit()
        db.session.delete(userPurchase)
        db.session.commit()
        db.session.delete(purchase)
        db.session.commit()
        return redirect(url_for("index"))
    except Exception as e:
        db.session.rollback()
        print(e)
        return redirect(url_for("index"))


@app.route('/transactions')
def transactions():
    return render_template("transactions.html")


@app.route('/categorise')
def categorise():
    return render_template("transactions.html")
