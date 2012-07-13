from django import forms


class SearchForm(forms.Form):
    query = forms.CharField(
        label=u"Name or keyword",
        widget=forms.TextInput(attrs={'size': 40, 'display': 'block'})
    )
