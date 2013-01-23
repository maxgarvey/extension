from django import forms

class lookup_form(forms.Form):
    '''
        lookup form only has one field, the username that will be queried.
    '''
    username = forms.CharField(max_length=100, required=True)

class extension_form(forms.Form):
    '''
        extend form also only has one field, the custom date. If one year
        option is selected, then it will show up in the post data for the form
        submission.
    '''
    custom_extend = forms.CharField(max_length=25, required=False)
