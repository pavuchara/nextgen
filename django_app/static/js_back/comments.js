const commentForm = document.forms.commentForm;
const commentFormContent = commentForm.body;
const commentFormParentInput = commentForm.parent;
const commentFormSubmit = commentForm.commentSubmit;
const commentPostId = commentForm.getAttribute('data-post-id');

commentForm.addEventListener('submit', createComment);

replyUser();

function replyUser() {
  document.querySelectorAll('.btn-reply').forEach(e => {
    e.addEventListener('click', replyComment);
  });
}

function replyComment() {
  const commentUsername = this.getAttribute('data-comment-username');
  const commentMessageId = this.getAttribute('data-comment-id');
  commentFormContent.value = `${commentUsername}, `;
  commentFormParentInput.value = commentMessageId;
}

function setupEventHandlers() {
  document.querySelectorAll('.btn-delete-comment').forEach(button => {
    button.addEventListener('click', deleteComment);
  });
}

setupEventHandlers();

async function createComment(event) {
  event.preventDefault();
  if (!grecaptcha.getResponse()) {
    alert('Пожалуйста, введите капчу');
    return;
  }
  commentFormSubmit.disabled = true;
  commentFormSubmit.innerText = "Ожидаем ответа сервера";
  try {
    const response = await fetch(`/post/${commentPostId}/comments/create/`, {
      method: 'POST',
      headers: {
        'X-CSRFToken': csrftoken,
        'X-Requested-With': 'XMLHttpRequest',
      },
      body: new FormData(commentForm),
    });
    const comment = await response.json();
    const formattedDate = new Intl.DateTimeFormat('ru', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: 'numeric',
      minute: 'numeric',
      second: 'numeric',
    }).format(new Date(comment.create));
    console.log(comment);
    let commentTemplate = `<li class="card border-1 m-1">
                                <div class="row">
                                  <div class="col-md-1">
                                    <img src="${comment.avatar}" style="width: 50px;height: 50px;object-fit: cover;" alt="${comment.author}" class="rounded-circle m-2"/>
                                  </div>
                                  <div class="col-md-11">
                                    <div class="card-body">
                                      <span class="card-title">
                                        <a href="${comment.get_absolute_url}">${comment.author}</a>
                                        <time>${formattedDate}</time>
                                      </span>
                                      <p class="card-text">
                                        ${comment.body}
                                      </p>
                                      <a class="btn btn-sm btn-dark btn-reply" href="#commentForm" data-comment-id="${comment.id}" data-comment-username="${comment.author}">Ответить</a>
                                      <a class="btn btn-sm btn-danger btn-delete-comment" href="#commentForm" data-comment-id="${comment.id}">Удалить комментарий</a>
                                    </div>
                                  </div>
                                </div>
                              </li>`;
    document.querySelector('.nested-comments').insertAdjacentHTML("beforeend", commentTemplate);
    commentForm.reset()
    grecaptcha.reset()
    commentFormSubmit.disabled = false;
    commentFormSubmit.innerText = "Добавить комментарий";
    commentFormParentInput.value = null;
    replyUser();
    setupEventHandlers();
  } catch (error) {
    console.log(error)
  }
}

document.querySelectorAll('.btn-delete-comment').forEach(button => {
  button.addEventListener('click', deleteComment);
});

async function deleteComment(event) {
  event.preventDefault();
  const commentId = this.getAttribute('data-comment-id');
  try {
    const response = await fetch(`/post/${commentPostId}/comments/${commentId}/delete/`, {
      method: 'DELETE',
      headers: {
          'X-CSRFToken': getCookie('csrftoken'),
          'Content-Type': 'application/json',
      },
    });
    if (response.ok) {
      this.closest('.card').remove();
    } else {
      console.error('Ошибка при удалении комментария');
    }
  } catch (error) {
    console.error('Ошибка при отправке запроса на удаление комментария:', error);
  }
}
