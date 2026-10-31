from django import forms

class InvestigationForm(forms.Form):
    """
    Form for collecting investigation details.
    """
    victim_wallet_address = forms.CharField(
        label="Victim Wallet Address",
        max_length=42
    )
    target_wallet_address = forms.CharField(
        label="Target Wallet Address",
        max_length=42
    )
    transaction_hash = forms.CharField(
        label="Transaction Hash",
        max_length=66
    )
    investigation_start_date = forms.DateField(
        label="Investigation Start Date"
    )
    investigation_end_date = forms.DateField(
        label="Investigation End Date"
    )
