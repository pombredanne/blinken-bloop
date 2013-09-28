from django.core.urlresolvers import reverse_lazy
from django.utils.translation import ugettext_lazy as _

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Fieldset, Div, HTML
from crispy_forms.bootstrap import FormActions
import floppyforms as forms

from . import models

TIME_FORMAT = '%H:%M %p'


class EventForm(forms.ModelForm):
    start = forms.SplitDateTimeField(
        label=_('When does the event start?'),
        input_time_formats=[TIME_FORMAT],
        widget=forms.SplitDateTimeWidget(time_format=TIME_FORMAT)
    )
    end = forms.SplitDateTimeField(
        label=_('And when does it end?'),
        input_time_formats=[TIME_FORMAT],
        widget=forms.SplitDateTimeWidget(time_format=TIME_FORMAT)
    )

    class Meta:
        model = models.Event
        widgets = {
            'max_attendees': forms.NumberInput(attrs={'min': '0', 'max': '9999'}),
            'max_guests': forms.NumberInput(attrs={'min': '0', 'max': '99'}),
            'host': forms.HiddenInput
        }

    class Media:
        css = {
            'screen': (
                'vendor/pickadate/css/classic.css',
                'vendor/pickadate/css/classic.date.css',
                'vendor/pickadate/css/classic.time.css'
            )
        }
        js = (
            'vendor/pickadate/js/picker.js',
            'vendor/pickadate/js/picker.date.js',
            'vendor/pickadate/js/picker.time.js',
            'vendor/pickadate/js/legacy.js',
            'js/forms.js'
        )

    def __init__(self, *args, **kwargs):
        show_actions = kwargs.pop('show_actions', None)
        render_form_tag = kwargs.pop('render_form_tag', True)
        super(EventForm, self).__init__(*args, **kwargs)

        actions = HTML('')
        if show_actions:
            actions = FormActions(
                Div(
                    HTML('<a href="{0}" class="btn btn-lg btn-block btn-link">'
                         'Nevermind</a>'.format(
                             reverse_lazy('events:dashboard'))),
                    css_class='col-xs-12 col-md-4'
                ),
                Div(
                    Submit('save', _('Create'),
                           css_class='primary btn-lg btn-block'),
                    css_class='col-xs-12 col-md-4'
                )
            )

        self.helper = FormHelper()
        self.helper.form_method = u'POST'
        self.helper.form_tag = render_form_tag
        self.helper.label_class = 'col-lg-2'
        self.helper.field_class = 'col-lg-10'
        self.helper.layout = Layout(
            Fieldset(
                u'',
                u'host',
                u'title',
                u'location',
                u'description',
                Div(
                    Div(u'start', css_class=u'col-xs-12 col-md-4 no-horizontal'),
                    Div(u'end', css_class=u'col-xs-12 col-md-4 no-horizontal'),
                    css_class=u'row'
                ),
                Div(
                    Div(u'max_attendees', css_class=u'col-xs-12 col-md-4 no-horizontal'),
                    Div(u'max_guests', css_class=u'col-xs-12 col-md-4 no-horizontal'),
                    Div(u'cost', css_class=u'col-xs-12 col-md-4 no-horizontal'),
                    css_class=u'row'
                ),
            ),
            actions
        )

    def clean_end(self):
        data = self.cleaned_data['end']
        start = self.cleaned_data['start']

        if data < start:
            raise forms.ValidationError(
                _("Events can't end before they've started."))
        return data


class RSVPForm(forms.ModelForm):
    class Meta:
        model = models.RSVP

    def __init__(self, *args, **kwargs):
        event = kwargs.pop('event', None)
        user = kwargs.pop('user', None)
        super(RSVPForm, self).__init__(*args, **kwargs)

        actions = FormActions(
            Div(
                Submit('save', _('RSVP'),
                       css_class='primary btn-lg btn-block'),
                css_class='col-xs-12 col-md-6'
            )
        )

        self.helper = FormHelper()
        self.helper.form_method = u'POST'
        self.helper.form_tag = True
        self.helper.label_class = 'col-lg-2'
        self.helper.field_class = 'col-lg-10'
        self.helper.layout = Layout(
            Fieldset(
                u'',
                u'event',
                u'user',
                u'response',
                u'num_guests',
                u'notes',
            ),
            actions
        )

        self.fields['event'].initial = event.pk
        self.fields['event'].widget = forms.HiddenInput()
        self.fields['user'].initial = user.pk
        self.fields['user'].widget = forms.HiddenInput()
