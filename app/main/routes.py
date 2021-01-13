from datetime import datetime
from flask import render_template, flash, redirect, url_for, request, g, \
    jsonify, current_app
from flask_login import current_user, login_required
from flask_babel import _, get_locale
from app import db
from app.main.forms import EditProfileForm, EmptyForm, PostForm, SearchForm, \
    MessageForm, CreateThreadForm
from app.models import User, Post, Message, Notification, Board, Thread
from app.main import bp
import os
from PIL import Image
import inspect
import random, string
import app.models

@bp.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()
    g.search_form = SearchForm()
    g.locale = str(get_locale())
    
def pic_name(pic_form):
    pic_random = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
    _, f_ext = os.path.splitext(pic_form.filename)
    picture_name = pic_random + f_ext
    path_r = os.path.dirname(inspect.getfile(app.models))
    picture_path = os.path.join(path_r, 'static/avatars', picture_name)

    i = Image.open(pic_form)
    i.save(picture_path)

    return picture_name
    
@bp.route('/')
@bp.route('/index')
def index():
    boards = Board.query.order_by(Board.id)
    header_msg = 'View all boards'
    return render_template('board_index.html', title=_('Boards'),
                           boards=boards, header_msg=header_msg)

@bp.route('/followed')
@login_required
def followed():
    header_msg = 'Posts by followed users'
    page = request.args.get('page', 1, type=int)
    posts = current_user.followed_posts().paginate(
        page, current_app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('main.followed', page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('main.followed', page=posts.prev_num) \
        if posts.has_prev else None
    return render_template('followed.html', title=_('Followed Users'), 
                               posts=posts.items, next_url=next_url,
                               prev_url=prev_url, header_msg=header_msg)

@bp.route('/board/<title>')
def board(title):
    header_msg = title
    page = request.args.get('page', 1, type=int)
    board = Board.query.filter(Board.title == title).one()
    threads = Thread.query.filter(Thread.board_id == board.id).order_by \
        (Thread.timestamp).paginate(page, current_app.config['POSTS_PER_PAGE'], False)
    
    next_url = url_for('main.board', page=threads.next_num) \
        if threads.has_next else None
    prev_url = url_for('main.board', page=threads.prev_num) \
        if threads.has_prev else None   
    
    return render_template('board.html', title=_('board/<title>'), threads=threads.items, \
        next_url=next_url, prev_url = prev_url, header_msg = header_msg)

@bp.route('/thread/<title>', methods=['GET', 'POST'])
def thread(title):
    header_msg = title
    page = request.args.get('page', 1, type=int)
    thread = Thread.query.filter(Thread.title == title).one()
    body_msg = thread.description
    posts = Post.query.filter(Post.thread_id == thread.id).order_by \
        (Post.timestamp).paginate(page, current_app.config['POSTS_PER_PAGE'], False)

    next_url = url_for('main.thread', page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('main.thread', page=posts.prev_num) \
        if posts.has_prev else None   
    
    if current_user.is_authenticated:
        form = PostForm()
        if form.validate_on_submit():
            post = Post(body=form.post.data, author=current_user,
                        thread_id = thread.id)       
            db.session.add(post)   
            db.session.commit()
            flash(_('Your post is now live!'))
            return redirect(url_for('main.thread', title = thread.title))
        return render_template('thread.html', title=_('thread/<title>'), posts=posts.items, \
                next_url=next_url, prev_url = prev_url, header_msg = header_msg, form = form,\
                    body_msg = body_msg)
    else:
        return render_template('thread.html', title=_('thread/<title>'), posts=posts.items, \
        next_url=next_url, prev_url = prev_url, header_msg = header_msg,  body_msg = body_msg)

@bp.route('/create_thread/<board_title>', methods=['GET', 'POST'])
@login_required
def create_thread(board_title):
    board = Board.query.filter(Board.title == board_title).one()
    form = CreateThreadForm()
    
    if form.validate_on_submit():
        thread = Thread( title=form.name.data, description = form.description.data, \
                        board=board, author=current_user)
        db.session.add(thread)
        db.session.commit()
        flash(_('Your post has been created.'))
        return redirect(url_for('main.board', title=board_title))

    return render_template('create_thread.html', _title=('Create Thread'),
                           form=form)

@bp.route('/create_board', methods=['GET', 'POST'])
@login_required
def create_board():
    form = CreateThreadForm()
    
    if form.validate_on_submit():
        bn = Board( title=form.name.data, body = form.description.data)
        db.session.add(bn)
        db.session.commit()
        flash(_('Your board has been created.'))
        return redirect(url_for('main.index'))

    return render_template('create_board.html',
                           form=form)

@bp.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    posts = user.posts.order_by(Post.timestamp).paginate(
        page, current_app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('main.user', username=user.username,
                       page=posts.next_num) if posts.has_next else None
    prev_url = url_for('main.user', username=user.username,
                       page=posts.prev_num) if posts.has_prev else None
    form = EmptyForm()
    return render_template('user.html', user=user, posts=posts.items,
                           next_url=next_url, prev_url=prev_url, form=form)

@bp.route('/user/<username>/popup')
@login_required
def user_popup(username):
    user = User.query.filter_by(username=username).first_or_404()
    form = EmptyForm()
    return render_template('user_popup.html', user=user, form=form)

@bp.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        if form.avatar_pic.data:
            avatar_pic = pic_name(form.avatar_pic.data)
            current_user.prof_pic = avatar_pic
        db.session.commit()
        flash(_('Your changes have been saved.'))
        return redirect(url_for('main.edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title=_('Edit Profile'),
                           form=form)

@bp.route('/follow/<username>', methods=['POST'])
@login_required
def follow(username):
    form = EmptyForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=username).first()
        if user is None:
            flash(_('User %(username)s not found.', username=username))
            return redirect(url_for('main.index'))
        if user == current_user:
            flash(_('You cannot follow yourself!'))
            return redirect(url_for('main.user', username=username))
        current_user.follow(user)
        db.session.commit()
        flash(_('You are following %(username)s!', username=username))
        return redirect(url_for('main.user', username=username))
    else:
        return redirect(url_for('main.index'))

@bp.route('/unfollow/<username>', methods=['POST'])
@login_required
def unfollow(username):
    form = EmptyForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=username).first()
        if user is None:
            flash(_('User %(username)s not found.', username=username))
            return redirect(url_for('main.index'))
        if user == current_user:
            flash(_('You cannot unfollow yourself!'))
            return redirect(url_for('main.user', username=username))
        current_user.unfollow(user)
        db.session.commit()
        flash(_('You are not following %(username)s.', username=username))
        return redirect(url_for('main.user', username=username))
    else:
        return redirect(url_for('main.index'))

@bp.route('/search')
def search():
    if not g.search_form.validate():
        return redirect(url_for('main.index'))
    page = request.args.get('page', 1, type=int)
    posts, total = Post.search(g.search_form.q.data, page,
                               current_app.config['POSTS_PER_PAGE'])
    next_url = url_for('main.search', q=g.search_form.q.data, page=page + 1) \
        if total > page * current_app.config['POSTS_PER_PAGE'] else None
    prev_url = url_for('main.search', q=g.search_form.q.data, page=page - 1) \
        if page > 1 else None
    return render_template('search.html', title=_('Search'), posts=posts,
                           next_url=next_url, prev_url=prev_url)


@bp.route('/send_message/<recipient>', methods=['GET', 'POST'])
@login_required
def send_message(recipient):
    user = User.query.filter_by(username=recipient).first_or_404()
    form = MessageForm()
    if form.validate_on_submit():
        msg = Message(author=current_user, recipient=user,
                      body=form.message.data)
        db.session.add(msg)
        user.add_notification('unread_message_count', user.new_messages())
        db.session.commit()
        flash(_('Your message has been sent.'))
        return redirect(url_for('main.user', username=recipient))
    return render_template('send_message.html', title=_('Send Message'),
                           form=form, recipient=recipient)

@bp.route('/messages')
@login_required
def messages():
    current_user.last_message_read_time = datetime.utcnow()
    current_user.add_notification('unread_message_count', 0)
    db.session.commit()
    page = request.args.get('page', 1, type=int)
    messages = current_user.messages_received.order_by(
        Message.timestamp).paginate(
            page, current_app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('main.messages', page=messages.next_num) \
        if messages.has_next else None
    prev_url = url_for('main.messages', page=messages.prev_num) \
        if messages.has_prev else None
    return render_template('messages.html', messages=messages.items,
                           next_url=next_url, prev_url=prev_url)

@bp.route('/notifications')
@login_required
def notifications():
    since = request.args.get('since', 0.0, type=float)
    notifications = current_user.notifications.filter(
        Notification.timestamp > since).order_by(Notification.timestamp.asc())
    return jsonify([{
        'name': n.name,
        'data': n.get_data(),
        'timestamp': n.timestamp
    } for n in notifications])