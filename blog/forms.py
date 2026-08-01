from django import forms
from .models import Comment, Category
from mptt.forms import TreeNodeChoiceField


class NewCommentForm(forms.ModelForm):

    parent = TreeNodeChoiceField(queryset=Comment.objects.all(), required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['parent'].widget = forms.HiddenInput()
        self.fields['parent'].label = ''
        self.fields['parent'].required = False

    class Meta:
        model = Comment
        fields = ('name', 'email', 'parent', 'content')
        widgets = {
            'name': forms.TextInput(attrs={'class': 'w-full rounded border border-slate-300 px-3 py-2 text-sm text-slate-900 focus:border-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-100', 'placeholder': 'Votre nom'}),
            'email': forms.TextInput(attrs={'class': 'w-full rounded border border-slate-300 px-3 py-2 text-sm text-slate-900 focus:border-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-100', 'placeholder': 'Votre email'}),
            'content': forms.Textarea(attrs={'class': 'w-full rounded border border-slate-300 px-3 py-2 text-sm text-slate-900 focus:border-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-100', 'rows': 4, 'placeholder': 'Écrivez votre commentaire...'}),
        }

    def save(self, *args, **kwargs):
        Comment.objects.rebuild()
        return super().save(*args, **kwargs)


class PostSearchForm(forms.Form):
    q = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'w-full rounded border border-slate-300 px-3 py-2 text-sm text-slate-900 focus:border-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-100', 'placeholder': 'Rechercher un article'})
    )
    c = forms.ModelChoiceField(
        queryset=Category.objects.all().order_by('name'),
        required=False,
        empty_label='Toutes les catégories',
        widget=forms.Select(attrs={'class': 'w-full rounded border border-slate-300 bg-white px-3 py-2 text-sm text-slate-900 focus:border-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-100'})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['c'].label = 'Catégorie'
        self.fields['q'].label = 'Rechercher'
        self.fields['q'].widget.attrs.update({'aria-label': 'Recherche'})