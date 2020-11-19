
"""
Columbia's COMS W4111.001 Introduction to Databases
Example Webserver
To run locally:
    python server.py
Go to http://localhost:8111 in your browser.
A debugger such as "pdb" may be helpful for debugging.
Read about it online.
"""
import os
  # accessible as a variable in index.html:
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, Response, url_for
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import InputRequired, Email, Length

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, IntegerField, SelectField, FormField, DateField, SelectMultipleField
from wtforms.validators import InputRequired, Email, Length, NumberRange
from flask_bootstrap import Bootstrap

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)
app.config['SECRET_KEY'] = os.urandom(24)
Bootstrap(app)

class LoginForm(FlaskForm):
  username = StringField('username', validators=[InputRequired()])
  password = PasswordField('password', validators=[InputRequired()])
  remember = BooleanField('remember me')

DATABASEURI = "postgresql://dsl2162:dsl2162zo2146@34.75.150.200/proj1part2"

# This line creates a database engine that knows how to connect to the URI above.
engine = create_engine(DATABASEURI)

# Example of running queries in your database
# Note that this will probably not work if you already have a table named 'test' in your database, containing meaningful data. This is only an example showing you how to run queries in your database using SQLAlchemy.
#
# engine.execute("""CREATE TABLE IF NOT EXISTS test (
#   id serial,
#   name text
# );""")
# engine.execute("""INSERT INTO test(name) VALUES ('grace hopper'), ('alan turing'), ('ada lovelace');""")

@app.before_request
def before_request():
  """
  This function is run at the beginning of every web request 
  (every time you enter an address in the web browser).
  We use it to setup a database connection that can be used throughout the request.

  The variable g is globally accessible.
  """
  try:
    g.conn = engine.connect()
  except:
    print("uh oh, problem connecting to database")
    import traceback; traceback.print_exc()
    g.conn = None

@app.teardown_request
def teardown_request(exception):
  """
  At the end of the web request, this makes sure to close the database connection.
  If you don't, the database could run out of memory!
  """
  try:
    g.conn.close()
  except Exception as e:
    pass

# @app.route is a decorator around index() that means:
#   run index() whenever the user tries to access the "/" path using a GET request
#
# If you wanted the user to go to, for example, localhost:8111/foobar/ with POST or GET then you could use:
#
#       @app.route("/foobar/", methods=["POST", "GET"])
#
# PROTIP: (the trailing / in the path is important)
# 
# see for routing: http://flask.pocoo.org/docs/0.10/quickstart/#routing
# see for decorators: http://simeonfranklin.com/blog/2012/jul/1/python-decorators-in-12-steps/
#

@app.route('/')
def index():
  """
  request is a special object that Flask provides to access web request information:

  request.method:   "GET" or "POST"
  request.form:     if the browser submitted a form, this contains the data in the form
  request.args:     dictionary of URL arguments, e.g., {a:1, b:2} for http://localhost?a=1&b=2

  See its API: http://flask.pocoo.org/docs/0.10/api/#incoming-request-data
  """

  # DEBUG: this is debugging code to see what request looks like
  print(request.args)

  # example of a database query
  # cursor = g.conn.execute("SELECT name FROM test")
  # names = []
  # for result in cursor:
  #   names.append(result['name'])  # can also be accessed using result[0]
  # cursor.close()

  #
  # Flask uses Jinja templates, which is an extension to HTML where you can
  # pass data to a template and dynamically generate HTML based on the data
  # (you can think of it as simple PHP)
  # documentation: https://realpython.com/blog/python/primer-on-jinja-templating/
  #
  # You can see an example template in templates/index.html
  #
  # context are the variables that are passed to the template.
  # for example, "data" key in the context variable defined below will be
  # accessible as a variable in index.html:
  #
  #     # will print: [u'grace hopper', u'alan turing', u'ada lovelace']
  #     <div>{{data}}</div>
  #
  #     # creates a <div> tag for each element in data
  #     # will print:
  #     #
  #     #   <div>grace hopper</div>
  #     #   <div>alan turing</div>
  #     #   <div>ada lovelace</div>
  #     #
  #     {% for n in data %}
  #     <div>{{n}}</div>
  #     {% endfor %}
  #
  # context = dict(data = names)

  # render_template looks in the templates/ folder for files.
  # for example, the below file reads template/index.html
  #
  # return render_template("index.html", **context)
  return render_template("index.html")

# This is an example of a different path.  You can see it at:
# 
#     localhost:8111/another
#
# Notice that the function name is another() rather than index()
# The functions for each app.route need to have different names
@app.route('/login', methods=['GET', 'POST'])
def login():
  form = LoginForm()
  if form.validate_on_submit():
    uid = form.username.data
    pwd = form.password.data
    user = g.conn.execute('SELECT * FROM User_From WHERE uname=%s', uid).first()
    if user:
      if user.password == pwd:
        return '<h1> Success </h1>'
    return '<h1> Invalid username or password </h1>'
  return render_template('login.html', form=form)

# Example of adding new data to the database
@app.route('/add', methods=['GET'])
def add():
  name = request.form['name']
  g.conn.execute('INSERT INTO test(name) VALUES (%s)', name)
  return redirect('/')

# Users logging into the database
# @app.route('/login/submit', methods=['GET'])
# def add():
#   name = request.form['name']
#   g.conn.execute('INSERT INTO test(name) VALUES (%s)', name)
#   return redirect('/')

# # Searching for sequence and occurrence in database
# @app.route('/add', methods=['POST'])
# def add():
#   name = request.form['name']
#   g.conn.execute('INSERT INTO test(name) VALUES (%s)', name)
#   return redirect('/')


class RegistrationForm(FlaskForm):
  uname = StringField('Username', validators=[InputRequired(), Length(max=20)])
  email = StringField('Email', validators=[InputRequired(), Email(), Length(max=50)])
  password = PasswordField('Password', validators=[InputRequired(), Length(max=20)])
  institution = SelectField('institution', choices=[(1,'University'),(0,'Organization')], coerce=int)
  since = DateField('since')
  position = StringField('Position', validators=[Length(max=20)])
  iname = StringField('institution name', validators=[InputRequired(),Length(max=50)])
  country = StringField('country', validators=[InputRequired(), Length(max=20)])
  state = StringField('state', validators=[Length(max=20)])
  zipcode = IntegerField('zipcode', validators=[NumberRange(min=9999, max=99999)])
  division = StringField('division', validators=[Length(max=20)])
  department = StringField('department', validators=[Length(max=20)])
  lab = StringField('lab', validators=[Length(max=20)])


@app.route("/registration", methods=['GET', 'POST'])
def register():
  error = None
  form = RegistrationForm()
  if form.validate_on_submit():
    since = form.since.data
    uname = form.uname.data
    email = form.email.data
    pwd = form.password.data
    inst = form.institution.data
    pos = form.position.data
    iname = form.iname.data
    coun = form.country.data
    st = form.state.data
    zcode = form.zipcode.data
    div = form.division.data
    dept = form.department.data
    lab = form.lab.data

    user = g.conn.execute('SELECT * FROM user_from WHERE uname=%s', uname).first()
    e = g.conn.execute('SELECT * FROM user_from WHERE email=%s', email).first()
    if user:
      error = '<h1> This username is already in use.</h1>'
      return render_template('registration.html', error=error, form=form)
    if e:
      error = '<h1> This email is already registered.</h1>'
      return render_template('registration.html', error=error, form=form)

    g.conn.execute('INSERT INTO institution(iname, country, state, zipcode) VALUES(%s, %s, %s, %s)',iname, coun, st, zcode)
    g.conn.execute('INSERT INTO user_from(uname, email, password, since, position, iname, country) VALUES(%s, %s, %s, %s, %s, %s, %s)', uname, email, pwd, since, pos, iname, coun)
    if inst == 1:
      g.conn.execute('INSERT INTO university(iname, country, department, lab) VALUES(%s, %s, %s, %s)', iname, coun, dept, lab)
    else:
      g.conn.execute('INSERT INTO organisation(iname, country, division) VALUES(%s, %s, %s)',iname, coun, div)
    return redirect(url_for('home'))
  return render_template('registration.html', error=error, form=form)

@app.route('/onereference', methods=['GET', 'POST'])
def onereference():
  return redirect('/')

@app.route('/homesearch', methods=['GET', 'POST'])
def homesearch():
  if request.method == 'POST':
    gs = (request.form['genusspecies'])
    gs = gs.split()
    gen = gs[0]
    s = gs[1]
    occ = request.form['occurrence']
    seq = request.form['sequence']
    occ = int(occ)
    seq = int(seq)
    stbl = []
    has = []
    otbl = []

    if (occ and seq) or (not occ and not seq):
      cursor = g.conn.execute('SELECT accession_no FROM has WHERE genus=(%s) and species=(%s)', gen, s)
      for n in cursor:
        has.append(n)
      cursor.close()
      for no in has:
        ref = g.conn.execute('SELECT doi FROM sequence_source WHERE accession_no=(%s)', no[0]).first()
        cursor = g.conn.execute('SELECT * FROM sequence_source n INNER JOIN reference r USING (doi) WHERE n.accession_no=(%s) and r.doi=(%s)', no[0], ref[0])
        val = cursor.first()
        stbl += [val]
        cursor.close()
      cursor = g.conn.execute('SELECT * FROM occ_records WHERE genus=(%s) and species=(%s)', gen, s)
      for n in cursor:
        otbl.append(n)
      cursor.close()
      return render_template('search.html', stbl=stbl, otbl=otbl)

    elif occ:
      cursor = g.conn.execute('SELECT * FROM occ_records WHERE genus=(%s) and species=(%s)', gen, s)
      for n in cursor:
        otbl.append(n)
      cursor.close()
      return render_template('search.html', otbl=otbl)

    elif seq:
      cursor = g.conn.execute('SELECT accession_no FROM has WHERE genus=(%s) and species=(%s)', gen, s)
      for n in cursor:
        has.append(n)
      cursor.close()
      for no in has:
        ref = g.conn.execute('SELECT doi FROM sequence_source WHERE accession_no=(%s)', no[0]).first()
        cursor = g.conn.execute('SELECT * FROM sequence_source n INNER JOIN reference r USING (doi) WHERE n.accession_no=(%s) and r.doi=(%s)',
                                no[0], ref[0])
        val = cursor.first()
        stbl += [val]
        cursor.close()
      return render_template('search.html', stbl=stbl)

  return redirect('/')

class SearchForm(FlaskForm):
  king = BooleanField('Kingdom')
  kings = SelectField('Kingdom Selection')
  phy = BooleanField('Phylum')
  phys = SelectField('Phylum Selection')
  cl = BooleanField('Class')
  cls = SelectField('Class Selection')
  ord = BooleanField('Orders')
  ords = SelectField('Orders Selection')
  fam = BooleanField('Family')
  fams = SelectField('Family Selection')
  gen = BooleanField('Genus')
  gens = SelectField('Genus Selection')
  spe = BooleanField('Species')
  spes = SelectField('Species Selection')
  seq = BooleanField('Sequence')

  sty = BooleanField('Sequence Type')
  stys = SelectField('Sequence Type Selection')
  bp = BooleanField('BP')
  bps = SelectField('BP Selection')
  occ = BooleanField('Occurrence')

  oty = BooleanField('Occurence Type')
  otys = SelectField('Occurrence Type Selection')
  loc = BooleanField('Location')
  locs = SelectField('Location Selection')

@app.route('/advancesearch', methods=['GET', 'POST'])
def advancesearch():
  error = None
  form = SearchForm()
  form.kings.choices = [x[0] for x in g.conn.execute('SELECT DISTINCT ON (kingdom) kingdom FROM organism')]
  form.phys.choices = [x[0] for x in g.conn.execute('SELECT DISTINCT ON (phylum) phylum FROM organism')]
  form.cls.choices = [x[0] for x in g.conn.execute('SELECT DISTINCT ON (class) class FROM organism')]
  form.ords.choices = [x[0] for x in g.conn.execute('SELECT DISTINCT ON (orders) orders FROM organism')]
  form.fams.choices = [x[0] for x in g.conn.execute('SELECT DISTINCT ON (family) family FROM organism')]
  form.gens.choices = [x[0] for x in g.conn.execute('SELECT DISTINCT ON (genus) genus FROM organism')]
  form.spes.choices = [x[0] for x in g.conn.execute('SELECT DISTINCT ON (species) species FROM organism')]
  form.stys.choices = [x[0] for x in g.conn.execute('SELECT DISTINCT ON (type) type FROM sequence_source')]
  form.bps.choices = [x[0] for x in g.conn.execute('SELECT DISTINCT ON (bp) bp FROM sequence_source')]
  form.otys.choices = [x[0] for x in g.conn.execute('SELECT DISTINCT ON (type) type FROM occ_records')]
  form.locs.choices = [x[0] for x in g.conn.execute('SELECT DISTINCT ON (location) location FROM occ_records')]
  
  if form.validate_on_submit():
    l=[]
    stbl = []
    otbl = []
    dorg = {"kingdom":(form.king.data,form.kings.data), "phylum":(form.phy.data,form.phys.data), "class":(form.cl.data,form.cls.data),
            "orders":(form.ord.data,form.ords.data), "family":(form.fam.data,form.fams.data), "genus":(form.gen.data,form.gens.data),
            "species":(form.spe.data,form.spes.data)}
    dseq = {'1':(form.sty.data,form.stys.data), '2':(form.bp.data,form.bps.data)}
    docc = {'1':(form.oty.data,form.otys.data), '2':(form.loc.data,form.locs.data)}

    for data in dorg.keys():
      if dorg[data][0] == True:
        pred = dorg[data][1]
        search = data
        l = [x for x in g.conn.execute('SELECT genus, species FROM organism WHERE '+search+ '=(%s)', pred)]
        break
    if form.seq.data:
      if l:
        t = [x for x in g.conn.execute('SELECT accession_no FROM has WHERE genus=(%s) and species=(%s)', l[0][0], l[0][1])]
      else:
        t = [x for x in g.conn.execute('SELECT accession_no FROM has')]

      if dseq['1'][0] and dseq['2'][0]:
        for no in t:
          ref = g.conn.execute('SELECT doi FROM sequence_source WHERE accession_no=(%s) and type=(%s) and bp=(%s)',
                               no[0], dseq['1'][1], dseq['2'][1]).first()
          stbl += [g.conn.execute('SELECT * FROM sequence_source n INNER JOIN reference r USING (doi) WHERE n.accession_no=(%s) and n.type=(%s) and n.bp=(%s) and r.doi=(%s)',
                                  no[0], dseq['1'][1], dseq['2'][1], ref[0]).first()]
      elif dseq['1'][0]:
        for no in t:
          ref = g.conn.execute('SELECT doi FROM sequence_source WHERE accession_no=(%s) and type=(%s)',
                               no[0], dseq['1'][1]).first()
          stbl += [g.conn.execute(
            'SELECT * FROM sequence_source n INNER JOIN reference r USING (doi) WHERE n.accession_no=(%s) and n.type=(%s) and r.doi=(%s)',
            no[0], dseq['1'][1], ref[0]).first()]
      elif dseq['2'][0]:
        for no in t:
          ref = g.conn.execute('SELECT doi FROM sequence_source WHERE accession_no=(%s) and bp=(%s)',
                               no[0], dseq['2'][1]).first()
          stbl += [g.conn.execute(
            'SELECT * FROM sequence_source n INNER JOIN reference r USING (doi) WHERE n.accession_no=(%s) and n.bp=(%s) and r.doi=(%s)',
            no[0], dseq['2'][1], ref[0]).first()]

      else:
        for no in t:
          ref = g.conn.execute('SELECT doi FROM sequence_source WHERE accession_no=(%s)',
                               no[0]).first()
          stbl += [g.conn.execute('SELECT * FROM sequence_source n INNER JOIN reference r USING (doi) WHERE n.accession_no=(%s) and r.doi=(%s)',
            no[0], ref[0]).first()]

    if form.occ.data:
      if l:
        if docc['1'][0] and docc['2'][0]:
          otbl += [x for x in g.conn.execute(
            'SELECT * FROM occ_records WHERE genus=(%s) and species=(%s) and type=(%s) and location=(%s)',
            l[0][0], l[0][1], docc['1'][1], docc['2'][1])]
        elif docc['1'][0]:
          otbl += [x for x in
                   g.conn.execute('SELECT * FROM occ_records WHERE genus=(%s) and species=(%s) and type=(%s)',
                                  l[0][0], l[0][1], docc['1'][1])]

        elif docc['2'][0]:
          otbl += [x for x in
                   g.conn.execute('SELECT * FROM occ_records WHERE genus=(%s) and species=(%s) and location=(%s) ',
                                  l[0][0], l[0][1], docc['2'][1])]

        else:
          otbl += [x for x in g.conn.execute('SELECT * FROM occ_records WHERE genus=(%s) and species=(%s)', l[0][0], l[0][1])]

      else:
        if docc['1'][0] and docc['2'][0]:
          otbl += [x for x in g.conn.execute(
            'SELECT * FROM occ_records WHERE type=(%s) and location=(%s)', docc['1'][1], docc['2'][1])]
        elif docc['1'][0]:
          otbl += [x for x in
                   g.conn.execute('SELECT * FROM occ_records WHERE type=(%s)',docc['1'][1])]

        elif docc['2'][0]:
          otbl += [x for x in
                   g.conn.execute('SELECT * FROM occ_records WHERE location=(%s) ', docc['2'][1])]

        else:
          otbl += [x for x in g.conn.execute('SELECT * FROM occ_records')]

    if form.seq.data == False and form.occ.data == False:
      if l:
        t = [x for x in g.conn.execute('SELECT accession_no FROM has WHERE genus=(%s) and species=(%s)', l[0][0], l[0][1])]
        otbl += [x for x in
                 g.conn.execute('SELECT * FROM occ_records WHERE genus=(%s) and species=(%s)', l[0][0], l[0][1])]
      else:
        t = [x for x in g.conn.execute('SELECT accession_no FROM has')]
        otbl += [x for x in g.conn.execute('SELECT * FROM occ_records')]

      for no in t:
        ref = g.conn.execute('SELECT doi FROM sequence_source WHERE accession_no=(%s)',
                             no[0]).first()
        stbl += [g.conn.execute(
          'SELECT * FROM sequence_source n INNER JOIN reference r USING (doi) WHERE n.accession_no=(%s) and r.doi=(%s)',
          no[0], ref[0]).first()]



    return render_template('search.html', stbl=stbl, otbl=otbl)


  return render_template('advancesearch.html', error=error, form=form)


if __name__ == "__main__":
  import click

  @click.command()
  @click.option('--debug', is_flag=True)
  @click.option('--threaded', is_flag=True)
  @click.argument('HOST', default='0.0.0.0')
  @click.argument('PORT', default=8111, type=int)
  def run(debug, threaded, host, port):
    """
    This function handles command line parameters.
    Run the server using:

        python server.py

    Show the help text using:

        python server.py --help

    """

    HOST, PORT = host, port
    print("running on %s:%d" % (HOST, PORT))
    app.run(host=HOST, port=PORT, debug=debug, threaded=threaded)

  run()