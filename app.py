
from flask import Flask, render_template, redirect, request, session, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
from flask_login import UserMixin, LoginManager, login_user, login_required, current_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash

import os, random

app = Flask(__name__)

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SECRET_KEY'] = 'testing123'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir,'database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# --------------------------------- DECLARE TABLES ---------------------------------------

class Item(db.Model):
  __tablename__ = 'item'
  id = db.Column(db.Integer, primary_key=True)
  item_name = db.Column(db.String(100), nullable=False)
  item_description = db.Column(db.Text, nullable=False)
  item_type = db.Column(db.String(100), nullable=False)
  item_buy_price = db.Column(db.Numeric(10, 2), nullable=False)
  item_sell_price = db.Column(db.Numeric(10, 2), nullable=False)
  item_level = db.Column(db.Integer, default=0, nullable=True)

  __mapper_args__ = {'polymorphic_on': item_type, 'polymorphic_identity': 'item'}

class Weapon(Item):
  __tablename__ = 'weapon'
  id = db.Column(db.Integer, db.ForeignKey('item.id'), primary_key=True)
  skill = db.Column(db.String(100), nullable=True)
  damage = db.Column(db.Integer, nullable=False)
  skill_damage = db.Column(db.Integer, nullable=True)
  evade_boost = db.Column(db.Float, nullable=False)
  crit_chance = db.Column(db.Float, nullable=False)
  strength = db.Column(db.Integer, default=10, nullable=False)

  __mapper_args__ = {'polymorphic_identity': 'weapon'}

class Buff(Item):
  __tablename__ = 'buff'
  id = db.Column(db.Integer, db.ForeignKey('item.id'), primary_key=True)
  buff_type = db.Column(db.String(100), nullable=False)
  buff_amount = db.Column(db.Float, nullable=False)
  intelligence = db.Column(db.Integer, default=10, nullable=False)

  __mapper_args__ = {'polymorphic_identity': 'buff'}

class Debuff(Item):
  __tablename__ = 'debuff'
  id = db.Column(db.Integer, db.ForeignKey('item.id'), primary_key=True)
  debuff_type = db.Column(db.String(100), nullable=False)
  debuff_amount = db.Column(db.Float, nullable=False)
  intelligence = db.Column(db.Integer, default=10, nullable=False)

  __mapper_args__ = {'polymorphic_identity': 'debuff'}

class Heal(Item):
  __tablename__ = 'heal'
  id = db.Column(db.Integer, db.ForeignKey('item.id'), primary_key=True)
  heal_value = db.Column(db.Float, nullable=False)

  __mapper_args__ = {'polymorphic_identity': 'heal'}

class Accounts(UserMixin, db.Model):
  id = db.Column(db.Integer, primary_key = True)
  username = db.Column(db.String(100), nullable = False)
  email = db.Column(db.String(100), nullable = False)
  password = db.Column(db.String(100), nullable = False)
  is_active = db.Column(db.Boolean, default=True, nullable = False)

  level = db.Column(db.Integer, default=1, nullable=False)             # Level of the account
  xp = db.Column(db.Integer, default=0, nullable=False)                # Experience Points
  health_points = db.Column(db.Integer, default=100, nullable=False)   # Health Points
  mana_points = db.Column(db.Integer, default=50, nullable=False)      # Mana Points
  evade_chance = db.Column(db.Float, default=5.0, nullable=False)      # Evade Chance (%)
  strength = db.Column(db.Integer, default=10, nullable=False)         # Strength Attribute
  intelligence = db.Column(db.Integer, default=10, nullable=False)     # Intelligence Attribute
  endurance = db.Column(db.Integer, default=10, nullable=False)        # Endurance Attribute
  upgrade_points = db.Column(db.Integer, default=0, nullable=False)    # Upgrade Points

  coins = db.Column(db.Integer, default=0, nullable=False)             # Coins Amount
  diamonds = db.Column(db.Integer, default=0, nullable=False)          # Diamonds Amount

  inventory_items = db.relationship('Inventory', backref='account', lazy=True)

class Inventory(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  account_id = db.Column(db.Integer, db.ForeignKey('accounts.id'), nullable=False)
  item_name = db.Column(db.String(100), nullable=False)
  item_description = db.Column(db.Text, nullable=False)
  item_type = db.Column(db.String(100), nullable=False)
  quantity = db.Column(db.Integer, nullable=True, default=0)
  item_value = db.Column(db.Float, nullable=False)

class Monster(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(100), nullable=False)
  health_points = db.Column(db.Integer, nullable=False)    # Health Points
  weapon_used = db.Column(db.String(100), nullable=False)  # Weapon used by the monster
  evade_chance = db.Column(db.Float, nullable=False)       # Evade Chance (%)
  debuff_skill = db.Column(db.String(100), nullable=True)  # Debuff skill the monster uses
  reward_coin = db.Column(db.Integer, nullable=False)      # Coin reward for defeating the monster
  reward_diamond = db.Column(db.Integer, nullable=True)   # Diamond reward for defeating the monster
  reward_xp = db.Column(db.Integer, nullable=False)        # XP reward for defeating the monster
  skill_use_chance = db.Column(db.Float, nullable=True)   # Chance of using a skill

# --------------------------------- COMMIT DATAS ---------------------------------------

@app.cli.command("delete-data")
def initialize_data():
   with app.app_context():
    db.drop_all()

@app.cli.command("initialize-data")
def initialize_data():
  with app.app_context():
    db.create_all()

    dragon = Monster(
        name="Fire Dragon",
        health_points=500,
        weapon_used="Fire Breath",
        evade_chance=20.0,
        debuff_skill="Burn",
        reward_coin=500,
        reward_diamond=5,
        reward_xp=550,
        skill_use_chance=30.0
    )

    goblin = Monster(
        name="Goblin",
        health_points=100,
        weapon_used="Simple Sword",
        evade_chance=10.0,
        reward_coin=150,
        reward_diamond=0,
        reward_xp=150,
        skill_use_chance=0
    )

    fire_breath = Weapon(
        item_name="Fire Breath",
        item_description="A fiery attack that scorches enemies.",
        item_type="weapon",
        skill="",
        damage=50,
        evade_boost=5.0,
        crit_chance=10.0,
        item_buy_price=0,
        item_sell_price=0
    )

    simple_sword = Weapon(
        item_name="Simple Sword",
        item_description="Universal sword, cheap, readily available anywhere",
        item_type="weapon",
        skill="",
        damage=20,
        evade_boost=0.0,
        crit_chance=10.0,
        item_buy_price=100,
        item_sell_price=80
    )
    
    burn = Debuff(
        item_name="Burn",
        item_description="A persistent damage-over-time effect caused by fire.",
        item_type="debuff",
        debuff_type="Health Reduction",
        debuff_amount=5,
        item_buy_price=0,
        item_sell_price=0
    )

    db.session.add(dragon)
    db.session.add(goblin)
    db.session.add(fire_breath)
    db.session.add(simple_sword)
    db.session.add(burn)
    db.session.commit()

# --------------------------------- ACCOUNT HANDLING ---------------------------------------

@login_manager.user_loader
def load_user(user_id):
  return Accounts.query.get(int(user_id))

@app.route("/")
def home():
  return render_template("index.html")

@app.route("/signup", methods=('GET', 'POST'))
def signup():
  if request.method == 'POST':
    username = request.form['username']
    email = request.form['email']
    password = request.form['password']
    account = Accounts.query.filter_by(email=email).first()
    if account:
      flash('Email address already exists!')
      return redirect(url_for('signup'))

    default_weapon = Weapon.query.filter_by(item_name="Simple Sword").first()
    new_account = Accounts(username=username, email=email, password=generate_password_hash(password,method='pbkdf2:sha256'))
    
    db.session.add(new_account)
    db.session.commit()

    inventory_item = Inventory(
      account_id = new_account.id,
      item_name = default_weapon.item_name,
      item_description = default_weapon.item_description,
      item_type = default_weapon.item_type,
      quantity = 1,
      item_value = default_weapon.item_sell_price
    )

    db.session.add(inventory_item)
    db.session.commit()

    return redirect(url_for("login"))
  return render_template("authentication/signup.html")

@app.route("/login")
def login():
  return render_template("authentication/login.html")

@app.route("/login", methods = ['POST'])
def login_post():
  email = request.form['email']
  password = request.form['password']
  remember = request.form.get('remember')
  account = Accounts.query.filter_by(email=email).first()
  
  if not account or not check_password_hash(account.password, password):
    flash('Please check your login details and try again.')
    return redirect(url_for('login'))

  login_user(account, remember=remember)
  return redirect(url_for("home"))

@app.route("/logout")
@login_required
def logout():
  logout_user()
  return redirect(url_for("home"))

# ----------------------------------------- MAIN MENU -----------------------------------------

@app.route("/main-menu")
@login_required
def main_menu():
  user_account = Accounts.query.filter_by(id=current_user.id).first()
  return render_template("main_menu.html", account=user_account)

@app.route("/stats")
@login_required
def stats():
  user_account = Accounts.query.filter_by(id=current_user.id).first()
  return render_template("stats.html", account=user_account)

@app.route("/inventory")
@login_required
def inventory():
    user_inventory = Inventory.query.filter_by(account_id=current_user.id).all()
    return render_template("inventory.html", inventory_items=user_inventory, user_account=current_user)

@app.route("/sell-item/<int:item_id>", methods=["POST"])
@login_required
def sell_item(item_id):
  item_to_sell = Inventory.query.filter_by(account_id=current_user.id, id=item_id).first()

  if item_to_sell:
    item_to_sell.quantity -= 1
    current_user.coins += int(item_to_sell.item_value)
    db.session.delete(item_to_sell)
    db.session.commit()
    flash(f"You sold {item_to_sell.item_name} for ${item_to_sell.item_value}!", "success")

  return redirect(url_for("inventory"))

@app.route("/shop", methods=["GET", "POST"])
@login_required
def shop():
  user_account = Accounts.query.filter_by(id=current_user.id).first()
  weapons = Weapon.query.all()

  if request.method == "POST":
    weapon_id = request.form.get("weapon_id")
    weapon = Weapon.query.get(weapon_id)

    if weapon and user_account.coins >= weapon.item_buy_price:
      user_account.coins = int(user_account.coins - weapon.item_buy_price)
      existing_item = Inventory.query.filter_by(account_id=user_account.id, item_name=weapon.item_name).first()

      if existing_item:
        existing_item.quantity += 1
        flash(f"You purchased another {weapon.item_name}!", "success")
      else:
        new_item = Inventory(
          account_id=user_account.id,
          item_name=weapon.item_name,
          item_description=weapon.item_description,
          item_type=weapon.item_type,
          quantity=1,
          item_value=weapon.item_sell_price
        )
        db.session.add(new_item)
        flash(f"You purchased {weapon.item_name}!", "success")
      db.session.commit()

    else:
      flash("Not enough coins or invalid item!", "danger")
    return redirect(url_for("shop"))
  return render_template("shop.html", weapons=weapons, user_account=user_account)

# ----------------------------------------- BATTLE SECTION -----------------------------------------

@app.route("/battle-choice", methods=["GET", "POST"])
@login_required
def battle_choice():
    user = Accounts.query.filter_by(id=current_user.id).first()
    monsters = Monster.query.all()

    if request.method == "POST":
        monster_name = request.form.get("monster_name")
        monster = Monster.query.filter_by(name=monster_name).first()

        if monster:
            session['player_hp'] = user.health_points
            session['max_player_hp'] = user.health_points

            session['monster_name'] = monster.name
            session['monster_hp'] = monster.health_points
            session['max_monster_hp'] = monster.health_points

            session['battle_log'] = ["Battle begins!"]
            return redirect(url_for('battle'))
        else:
            flash("Monster not found, please try again!", "danger")
            return redirect(url_for('battle_choice'))

    return render_template("battle/battle_choice.html", monsters=monsters)

# Battle route
@app.route("/battle", methods=['GET', 'POST'])
@login_required
def battle():
    player = Accounts.query.filter_by(id=current_user.id).first()
    monster = Monster.query.filter_by(name=session.get('monster_name')).first()

    if request.method == 'POST':
        action = request.form['action']
        player_hp = session.get('player_hp')
        monster_hp = session.get('monster_hp')
        max_player_hp = session.get('max_player_hp')
        max_monster_hp = session.get('max_player_hp')
        battle_log = session.get('battle_log', [])

        if action == 'attack':
            player_damage = random.randint(5, 20)
            monster_damage = random.randint(5, 15)
            monster_hp -= player_damage
            player_hp -= monster_damage
            battle_log.append(f"You dealt {player_damage} damage to the monster!")
            battle_log.append(f"The monster dealt {monster_damage} damage to you!")

        elif action == 'defend':
            monster_damage = random.randint(2, 10)
            player_hp -= monster_damage
            battle_log.append(f"You defended! The monster dealt only {monster_damage} damage!")

        # Update session
        session['player_hp'] = max(player_hp, 0)
        session['monster_hp'] = max(monster_hp, 0)
        session['battle_log'] = battle_log

        # Check for battle outcome
        if monster_hp <= 0:
            battle_log.append("You defeated the monster!")
        elif player_hp <= 0:
            battle_log.append("You were defeated by the monster!")

        session['battle_log'] = battle_log

    return render_template("battle/battle.html", 
    player_hp=session.get('player_hp'), max_player_hp = session.get('max_player_hp'), 
    monster_hp=session.get('monster_hp'), max_monster_hp = session.get('max_monster_hp'),
    battle_log=session.get('battle_log', []))

@app.route("/battle-finished", methods=["POST"])
@login_required
def battle_finished():
  account = Accounts.query.get(current_user.id)
  monster_name = session.get("monster_name")
  monster = Monster.query.filter_by(name=monster_name).first()
  user_hp = session.get('player_hp')
  monster_hp = session.get('monster_hp')

  if user_hp <= 0 or (user_hp <= monster_hp):
      result = "lose"

  elif monster_hp <= 0:
      result = "win"
      account.coins += monster.reward_coin
      account.diamonds += monster.reward_diamond
      account.xp += monster.reward_xp

      new_level = (account.xp // 1000) + 1
      if new_level > account.level:
          account.level = new_level
          account.upgrade_points += 1
          flash(f"Congratulations! You've leveled up to Level {new_level}!", "success")
      db.session.commit()

  else:
      result = "error"

  return render_template("battle/battle_finished.html", result=result, monster=monster, account=account)

# ----------------------------------------- BATTLE SECTION -----------------------------------------

# Running the app in development mode
if __name__ == "__main__":
  app.run(host="0.0.0.0",debug=True)