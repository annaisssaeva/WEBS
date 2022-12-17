#импортим все нужные модули
from flask import Flask, url_for, render_template, request, redirect
from sqlalchemy import func
from flask_sqlalchemy import SQLAlchemy

#создаем базу данных
db = SQLAlchemy()
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///pentagon.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.app = app
db.init_app(app)

#создаем класс для таблицы юзеров – там будут столбцы с
#айди, гендером, возрастом и образованием
class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    gender = db.Column(db.Text)
    education = db.Column(db.Text)
    age = db.Column(db.Integer)

#в таблице с вопросами 2 столбца – айди вопроса и сам текст
class Questions(db.Model):
    __tablename__ = 'questions'
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text)

#в таблице с ответами айди и ответы на каждый из трех вопросов
class Answers(db.Model):
    __tablename__ = 'answers'
    id = db.Column(db.Integer, primary_key=True)
    q1 = db.Column(db.Integer)
    q2 = db.Column(db.Integer)
    q3 = db.Column(db.Integer)


@app.before_first_request
def create_tables():
    db.create_all()

#при переходе на страницу /questions даем три вопроса
#и показываем страницу questions.html
@app.route('/questions')
def question_page():
    qu1 = Questions(id=1,
                   text="Сколько наград заслужил камбек Daisy?")
    qu2 = Questions(id=2,
                   text="Сколько наград заслужил камбек Feelin' Like?")
    qu3 = Questions(id=3,
                    text="Как вы оцениваете песню пентагон про лягушек?")
    db.session.add(qu1)
    db.session.add(qu2)
    db.session.add(qu3)
    questions = db.session.query(Questions)
    return render_template(
        'questions.html',
        questions = questions,
        qu3 = qu3
    )

#при переходе на начальную страницу отображаем index.html
@app.route('/index')
def index_page():
    return render_template('index.html')

#при переходе просто на сайт стразу переводим на /index
#(мне просто так было проще проверять в процессе)
@app.route('/')
def zero_page():
    return redirect(url_for('index_page'))

#после отправки ответов присваиваем юзеру его ответы в анкете
#про возраст6 образование и гендер
@app.route('/process', methods=['get'])
def answer_process():
    if not request.args:
        return redirect(url_for('question_page'))
    gender = request.args.get('gender')
    education = request.args.get('education')
    age = request.args.get('age')
    user = User(
        age=age,
        gender=gender,
        education=education
    )
    db.session.add(user)
    db.session.commit()
    db.session.refresh(user)
    #берем ответы на вопросы оанкеты и записываем их в Answers
    q1 = request.args.get('q1')
    q2 = request.args.get('q2')
    q3 = request.args.get('q3')
    answer = Answers(id=user.id, q1=q1, q2=q2, q3=q3)
    db.session.add(answer)
    db.session.commit()
    #выводим страницу с благодарностью
    return render_template('thanks.html')

#на странице статистики выводим всредний, минимальный
#и максимальный возраст и в зависимости от того, как люди
#отвечали на последний вопрос про лягушек выводим текст
@app.route('/stats')
def stats():
    all_info = {}
    age_stats = db.session.query(
        func.avg(User.age),
        func.min(User.age),
        func.max(User.age)
    ).one()
    all_info['age_mean'] = age_stats[0]
    all_info['age_min'] = age_stats[1]
    all_info['age_max'] = age_stats[2]
    all_info['total_count'] = User.query.count()
    if db.session.query(func.avg(Answers.q3)).one()[0] >= 2:
        all_info['q1_mean'] = "стэн_ки Пентагон или просто любят лягушек"
    else:
        all_info['q1_mean'] = "не любят ни Пентагон, ни лягушек"
    return render_template('results.html', all_info=all_info)

if __name__ == '__main__':
    app.run()