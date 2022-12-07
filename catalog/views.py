from django.contrib import messages
from django.shortcuts import render
from django.views import generic
from django.views.generic import FormView
from .models import Book, Author, BookInstance, Genre, Rating
from .forms import RatingForm
from django.shortcuts import redirect, get_object_or_404
from django.db.models import Sum
from django.contrib.auth.mixins import LoginRequiredMixin

# Create your views here.


def index(request):
    num_books = Book.objects.all().count()
    num_instances = BookInstance.objects.all().count()
    num_instances_available = BookInstance.objects.filter(
        status__exact=2).count()
    num_authors = Author.objects.count()
    num_visits = request.session.get('num_visits', 1)
    request.session['num_visits'] = num_visits + 1
    return render(request, 'index.html', context={
        'num_books': num_books,
        'num_instances': num_instances,
        'num_instances_available': num_instances_available,
        'num_authors': num_authors,
        'num_visits': num_visits
    })


class BookListView(generic.ListView):
    model = Book
    paginate_by = 10


class BookDetailView(generic.DetailView, FormView):
    model = Book

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        sum_marks = Rating.objects.filter(book=self.kwargs['pk']).aggregate(Sum('mark'))
        count_marks = Rating.objects.filter(book=self.kwargs['pk']).count()
        can_be_author = Rating.objects.filter(author=self.request.user).filter(book=self.kwargs['pk']).count() == 0
        if count_marks:
            context['mark'] = round(sum_marks['mark__sum'] / count_marks, 2)
        context['can_be_author'] = can_be_author
        return context

    def get_form(self, form_class=RatingForm):
        return form_class(**self.get_form_kwargs())

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        book = get_object_or_404(Book, pk=self.kwargs['pk'])
        if form.is_valid():
            mark = form.save(commit=False)
            mark.author = request.user
            mark.book = book
            mark.save()
            messages.success(request, 'Ваша оценка учтена!')
            return redirect('book-detail', pk=book.pk)
        else:
            return self.form_invalid(form)


class AuthorListView(generic.ListView):
    model = Author
    paginate_by = 10


class LoanedBooksByUserListView(LoginRequiredMixin, generic.ListView):
    model = BookInstance
    template_name = 'catalog/book_instance_list_borrowed_user.html'
    paginate_by = 10

    def get_queryset(self):
        return BookInstance.objects \
            .filter(borrower=self.request.user) \
            .filter(status__exact='7') \
            .order_by('due_back')


