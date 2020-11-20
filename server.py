
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
from flask import Flask, request, render_template, g, redirect, Response, url_for, session, flash
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from country_list import countries_for_language
from wtforms import StringField, PasswordField, BooleanField, IntegerField, SelectField, FormField, DateField, DateTimeField, FloatField, SelectField, SelectMultipleField
from wtforms.validators import InputRequired, Email, Length, NumberRange, Optional
import datetime

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)
app.config['SECRET_KEY'] = os.urandom(24)
Bootstrap(app)

class LoginForm(FlaskForm):
  username = StringField('Username', validators=[InputRequired()])
  password = PasswordField('Password', validators=[InputRequired()])
  remember = BooleanField('Remember me')

class RegistrationForm(FlaskForm):
  uname = StringField('Username', validators=[InputRequired(), Length(max=20)])
  email = StringField('Email', validators=[InputRequired(), Email(), Length(max=50)])
  password = PasswordField('Password', validators=[InputRequired(), Length(max=20)])
  institution = SelectField('Institution', choices=[(1,'University'),(0,'Organization')], coerce=int)
  position = StringField('Position', validators=[Length(max=20), Optional()])
  iname = StringField('Institution name', validators=[InputRequired(),Length(max=50)])
  country = StringField('Country', validators=[InputRequired(), Length(max=20)])
  state = StringField('State', validators=[Length(max=20)])
  zipcode = IntegerField('Zipcode', validators=[NumberRange(min=9999, max=99999), Optional()])
  division = StringField('Division', validators=[Length(max=20)])
  department = StringField('Department', validators=[Length(max=20)])
  lab = StringField('Lab', validators=[Length(max=20)])

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

# class SubmitForm(FlaskForm):
#   # add in organism field
#   kingdom = StringField('Kingdom', validators=[Length(max=20)])
#   phylum = StringField('Phylum', validators=[Length(max=20)])
#   org_class = StringField('Class', validators=[Length(max=20)])
#   order = StringField('Order', validators=[Length(max=20)])
#   family = StringField('Family', validators=[Length(max=20)])
#   genus = StringField('Genus', validators=[InputRequired(), Length(max=20)])
#   species = StringField('Species', validators=[InputRequired(), Length(max=20)])
  # submission_type = SelectField('Submission Type', choices=[(1,'Sequence'),(0,'Occurrence')], coerce=int)
  # # sequence and reference
  # seq_type = StringField('Sequence type', validators=[Length(max=100)])
  # bp = IntegerField('Number of base pairs', validators=[NumberRange(min=1, max=200000)])
  # seq = StringField('Sequence', validators=[Length(min=10, max=200000)])
  # acc_no = StringField('Accession number', validators=[Length(max=20)])
  # date = DateField('Date')
  # title = StringField('Article title', validators=[Length(max=500)])
  # doi = StringField('DOI', validators=[InputRequired(), Length(max=100)]) 
  # author = StringField('Author(s)', validators=[Length(max=500)])
  # journal = StringField('Journal', validators=[Length(max=100)])
  # volume = IntegerField('Volume', validators=[NumberRange(min=1)])
  # issue = IntegerField('Issue', validators=[NumberRange(min=1)])
  # journal_date = DateField('Article date')
  # page_from = IntegerField('Page from', validators=[NumberRange(min=1)])
  # page_to = IntegerField('Page to', validators=[Optional(), NumberRange(min=1)])
  # #occurrence field
  # time = DateTimeField('Occurrence time')
  # occ_type = SelectField(u'Occurrence type', choices=['preserved specimen', 'human observation', 'machine observation'])
  # country = dict(countries_for_language('en'))
  # location = SelectField(u'Country', choices=country.values())
  # latitude = FloatField('Latitude', validators=[NumberRange(-90.0, 90.0)])
  # longitude = FloatField('Longitude', validators=[NumberRange(min=-90, max=90)])

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

@app.route('/login', methods=['GET', 'POST'])
def login():
  error = None
  form = LoginForm()
  if form.validate_on_submit():
    uid = form.username.data
    pwd = form.password.data
    user = g.conn.execute('SELECT * FROM User_From WHERE uname=%s', uid).first()
    if user:
      session['user'] = { 'username': user.uname , 'email': user.email}
      # session['user']['email'] = user.email
      if user.password == pwd:
        return redirect(url_for('dashboard', uname=uid))
    error = 'Invalid username or password'
    return render_template('login.html', error=error)
  return render_template('login.html', form=form)

@app.route('/logout', methods=['GET'])
def logout():
    if 'user' in session:
        session.pop('user')
    return redirect('/')

# Example of adding new data to the database
# @app.route('/add', methods=['GET'])
# def add():
#   name = request.form['name']
#   g.conn.execute('INSERT INTO test(name) VALUES (%s)', name)
#   return redirect('/')

# Users logging into the database
# @app.route('/login/submit', methods=['GET'])
# def add():
#   name = request.form['name']
#   g.conn.execute('INSERT INTO test(name) VALUES (%s)', name)
#   return redirect('/')

@app.route('/<uname>/dashboard', methods=['GET', 'POST'])
def dashboard(uname):
  if not 'user' in session:
    return redirect('/login')
  uname = session['user']['username']
  return render_template('dashboard.html', uname=session['user']['username'])

@app.route('/<uname>/profile', methods=['GET', 'POST'])
def profile(uname):
  if not 'user' in session:
    return redirect('/login')

  if request.method == 'POST':
    pwd = ''
    inst = ''
    dep =''
    lab = ''
    div = ''
    pos = ''
    st = ''
    zc = ''
    coun = ''

    if 'password' in request.form:
      pwd = request.form['password']
    if 'institution' in request.form:
      inst = request.form['institution']
    if 'department' in request.form:
      dep = request.form['department']
    if 'lab' in request.form:
      lab = request.form['lab']
    if 'division' in request.form:
      div = request.form['division']
    if 'position' in request.form:
      pos = request.form['position']
    if 'state' in request.form:
      st = request.form['state']
    if 'zipcode' in request.form:
      zc = request.form['zipcode']
    if 'country' in request.form:
      coun = request.form['country']

    if pwd:
      g.conn.execute('UPDATE user_from SET password=(%s) WHERE uname=(%s)', pwd, session['user']['username'])


    if dep:
      itbl = g.conn.execute("SELECT * FROM User_From WHERE email=(%s)", session['user']['email']).first()
      g.conn.execute('UPDATE university SET department=(%s) WHERE iname=(%s)', dep, itbl[5])

    if lab:
      itbl = g.conn.execute("SELECT * FROM User_From WHERE email=(%s)", session['user']['email']).first()
      g.conn.execute('UPDATE university SET lab=(%s) WHERE iname=(%s)', lab, itbl[5])

    if div:
      itbl = g.conn.execute("SELECT * FROM User_From WHERE email=(%s)", session['user']['email']).first()
      g.conn.execute('UPDATE organisation SET division=(%s) WHERE iname=(%s)', div, itbl[5])

    if pos:
      g.conn.execute('UPDATE user_from SET position=(%s) WHERE uname=(%s)', pos, session['user']['username'])

    if st:
      itbl = g.conn.execute("SELECT * FROM User_From WHERE email=(%s)", session['user']['email']).first()
      g.conn.execute('UPDATE institution SET state=(%s) WHERE iname=(%s)', st, itbl[5])

    if zc:
      itbl = g.conn.execute("SELECT * FROM User_From WHERE email=(%s)", session['user']['email']).first()
      g.conn.execute('UPDATE institution SET zipcode=(%s) WHERE iname=(%s)', zc, itbl[5])



  uname = session['user']['username']
  cursor = g.conn.execute("SELECT * FROM User_From WHERE email=%s", session['user']['email'])
  user_data = []
  for result in cursor:
    user_data.append(result)
  cursor.close()
  cursor = g.conn.execute("SELECT state, zipcode FROM User_From u NATURAL JOIN Institution i WHERE u.iname=%s", user_data[0][5])
  inst_data = []
  for result in cursor:
    inst_data.append(result)
  cursor.close()
  cursor = g.conn.execute("SELECT department, lab FROM Institution i NATURAL JOIN University u WHERE i.iname=%s", user_data[0][5])
  uni_data = []
  for result in cursor:
    uni_data.append(result)
  cursor.close()
  cursor = g.conn.execute("SELECT division FROM Institution i NATURAL JOIN Organisation o WHERE i.iname=%s", user_data[0][5])
  org_data = []
  for result in cursor:
    org_data.append(result)
  cursor.close()

  return render_template('profile.html', uname=session['user']['username'], user_data=user_data, inst_data=inst_data, uni_data=uni_data, org_data=org_data)


@app.route('/<uname>/history', methods=['GET'])
def history(uname):
  if not 'user' in session:
    return redirect('/login')
  cursor = g.conn.execute("SELECT genus, species, time FROM Access WHERE email=%s", session['user']['email'])
  hist = []
  for result in cursor:
    hist.append(result)
  cursor.close()
  return render_template('history.html', hist=hist, uname=uname)

@app.route('/<uname>/submit', methods=['GET', 'POST'])
def submit(uname):
  if not 'user' in session:
    return redirect('/login')
  error = None
  country = dict(countries_for_language('en'))
  location = country.values()
  otype = ['preserved specimen', 'human observation', 'machine observation']

  if request.method == 'POST':
    kingdom = request.form['kingdom']
    phylum = request.form['phylum']
    org_class = request.form['org_class']
    order = request.form['order']
    family = request.form['family']
    genus = request.form['genus']
    species = request.form['species']

    seq_type = request.form['seq_type']
    bp = request.form['bp']
    seq = request.form['seq']
    acc_no = request.form['acc_no']
    title = request.form['title']
    doi = request.form['doi']
    author = request.form['author']
    journal = request.form['journal']
    volume = request.form['volume']
    issue = request.form['issue']
    journal_date = request.form['journal_date']
    page_from = request.form['page_from']
    page_to = request.form['page_to']
    time = request.form['time']
    occ_type = request.form['occ_type']
    location = request.form['location']
    latitude = request.form['latitude']
    longitude = request.form['longitude']
    sequence = 'sequence' in request.form
    occurrence = 'occurrence' in request.form

    cursor = g.conn.execute("SELECT * FROM Organism WHERE genus=%s AND species=%s", genus, species)
    org = []
    for result in cursor:
      org.append(result)
    cursor.close()
    print(org)
    if not org:
      g.conn.execute('INSERT INTO Organism VALUES(%s, %s, %s, %s, %s, %s, %s)', kingdom, phylum, org_class, order, family, genus, species)
    print("test2")

    if sequence == True:
      g.conn.execute('INSERT INTO Reference VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s)', title, doi, author, journal, volume, issue, journal_date, page_from, page_to)
      g.conn.execute('INSERT INTO Sequence_Source VALUES(%s, %s, %s, %s, NOW()::date, %s)', seq_type, bp, seq, acc_no, doi)
      g.conn.execute('INSERT INTO Has VALUES(%s, %s, %s)', genus, species, acc_no)
      g.conn.execute('INSERT INTO Submit_Sqn VALUES(%s, %s, %s, %s, NOW()::date)', session['user']['email'], genus, species, acc_no)
    if occurrence == True:
      g.conn.execute('INSERT INTO Occ_records VALUES(%s, %s, %s, %s, %s, %s, %s)', time, occ_type, location, latitude, longitude, genus, species)
      g.conn.execute('INSERT INTO Submit_Occ VALUES(%s, %s, %s, %s, %s, %s, NOW()::date)', session['user']['email'], time, latitude, longitude, genus, species)
    return redirect(url_for('dashboard', uname=session['user']['username']))  
  return render_template('submit.html', error=error, otype = otype, location=location)

@app.route("/registration", methods=['GET', 'POST'])
def register():
  error = None
  form = RegistrationForm()
  if form.validate_on_submit():
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
      error = 'This username is already in use.'
      return render_template('registration.html', error=error, form=form)
    if e:
      error = 'This email is already registered.'
      return render_template('registration.html', error=error, form=form)

    if not g.conn.execute('SELECT * FROM institution WHERE iname=(%s) and country=(%s)', iname, coun).first():
      g.conn.execute('INSERT INTO institution(iname, country, state, zipcode) VALUES(%s, %s, %s, %s)',iname, coun, st, zcode)
      if inst == 1:
        if dept and lab:
          g.conn.execute('INSERT INTO university(iname, country, department, lab) VALUES(%s, %s, %s, %s)', iname, coun,
                       dept, lab)
        elif dept:
          g.conn.execute('INSERT INTO university(iname, country, department, lab) VALUES(%s, %s, %s, NULL)', iname, coun,
                         dept)

        elif lab:
          g.conn.execute('INSERT INTO university(iname, country, department, lab) VALUES(%s, %s, NULL, %s)', iname, coun,
                         lab)
      else:
        if div:
          g.conn.execute('INSERT INTO organisation(iname, country, division) VALUES(%s, %s, %s)', iname, coun, div)

    g.conn.execute('INSERT INTO user_from(uname, email, password, since, position, iname, country) VALUES(%s, %s, %s, now(), %s, %s, %s)', uname, email, pwd, pos, iname, coun)

    return redirect('/login')
  return render_template('registration.html', error=error, form=form)

@app.route('/<uname>/homesearch', methods=['GET', 'POST'])
def homesearch(uname):
  if request.method == 'POST':
    gs = ''
    gen =''
    s = ''
    if 'genusspecies' in request.form:
      gs = (request.form['genusspecies'])
      if not gs:
        error = "Please enter a valid Genus species"
        if 'user' in session:
          return render_template('dashboard.html', uname=uname, error=error)
        return render_template('index.html', error=error)
      gs = gs.split()
      gen = gs[0]
      s = gs[1]

    occ = None
    if 'occurrence' in request.form:
      occ = request.form['occurrence']
      occ = int(occ)
    seq = None
    if 'sequence' in request.form:
      seq = request.form['sequence']
      seq = int(seq)
    stbl = []
    has = []
    otbl = []


    if len(gen) >20 or len(s) >20:
      error = "The input length for genus or species is too long."
      if 'user' in session:
        return render_template('dashboard.html', uname=uname, error=error)
      return render_template('index.html', error=error)

    if 'user' in session:
      h = 'loginsearch.html'
      t = datetime.datetime.now()
    else:
      h = 'search.html'

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
      if ('user' in session) and (stbl or otbl):
        usere = session['user']['email']
        g.conn.execute('INSERT INTO history(time) VALUES(%s)', t)
        g.conn.execute('INSERT INTO access(email,genus, species, time) VALUES(%s, %s, %s, %s)', usere, gen, s, t)

      return render_template(h, stbl=stbl, otbl=otbl, uname=uname)

    elif occ:
      cursor = g.conn.execute('SELECT * FROM occ_records WHERE genus=(%s) and species=(%s)', gen, s)
      for n in cursor:
        otbl.append(n)
      cursor.close()

      return render_template(h, otbl=otbl, uname=uname)

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

      return render_template(h, stbl=stbl, uname=uname)

  return redirect('/')

@app.route('/homesearch', methods=['GET', 'POST'])
def unloggedhomesearch():
  return homesearch(None)

@app.route('/<uname>/loginadvsearch', methods=['GET', 'POST'])
def loginadvsearch(uname):
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

    if 'user' in session and (otbl or stbl):
      tm = datetime.datetime.now()
      g.conn.execute('INSERT INTO history(time) VALUES(%s)', tm)
      usere = session['user']['email']
      dt = {}
      for x in stbl:
        lt = g.conn.execute('SELECT genus, species FROM has WHERE accession_no=(%s)', x[4]).first()
        dt[lt[0],lt[1]]=1
      for x in otbl:
        dt[(x[5],x[6])]= 1
      for k in dt.keys():
        g.conn.execute('INSERT INTO access(email,genus, species, time) VALUES(%s, %s, %s, %s)', usere, k[0], k[1], tm)
      return render_template('loginsearch.html', stbl=stbl, otbl=otbl, uname=uname)

    elif 'user' in session:
      return render_template('loginsearch.html', stbl=stbl, otbl=otbl, uname=uname)

    return render_template('search.html', stbl=stbl, otbl=otbl)

  if 'user' in session:
    return render_template('loginadvsearch.html', error=error, form=form, uname=uname)
  return render_template('advancesearch.html', error=error, form=form)

@app.route('/advancesearch', methods=['GET', 'POST'])
def unloggedadvsearch():
  return loginadvsearch(None)

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