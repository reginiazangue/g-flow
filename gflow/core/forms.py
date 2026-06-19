from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Project, Application, Message, Evaluation


class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)
    role = forms.ChoiceField(choices=[('student','Étudiant'),('teacher','Enseignant')])

    class Meta:
        model = User
        fields = ('username','first_name','last_name','email','role','password1','password2')


class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name','last_name','email','phone','department','bio','avatar','cv')


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ('title','description','domain','technologies','difficulty','status','max_students','deadline')
        widgets = {
            'description': forms.Textarea(attrs={'rows':5}),
            'deadline': forms.DateInput(attrs={'type':'date'}),
        }


class ApplicationForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ('motivation',)
        widgets = {'motivation': forms.Textarea(attrs={'rows':5, 'placeholder':'Expliquez pourquoi ce projet vous intéresse...'})}


class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ('recipient','subject','body','project')
        widgets = {'body': forms.Textarea(attrs={'rows':6})}


class EvaluationForm(forms.ModelForm):
    class Meta:
        model = Evaluation
        fields = ('grade','comment')
        widgets = {'comment': forms.Textarea(attrs={'rows':4})}
