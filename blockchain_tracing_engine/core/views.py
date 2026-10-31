from celery.result import AsyncResult
from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import render, redirect

# local imports
from .chain_trace import ChainTrace
from .forms import InvestigationForm
from .tasks import run_chain_trace


# Create your views here.
def home(request):
    return render(request, "core/landing.html")

def investigate(request):
    if request.method == "POST":
        form = InvestigationForm(request.POST)
        
        if form.is_valid():
            # extract form data
            trace_params = {
                "victim_wallet_address" : form.cleaned_data['victim_wallet_address'],
                "target_wallet_address" : form.cleaned_data['target_wallet_address'],
                "transaction_hash" : form.cleaned_data['transaction_hash'],
                "investigation_start_date" : form.cleaned_data['investigation_start_date'],
                "investigation_end_date" : form.cleaned_data['investigation_end_date']
            }

            try:
                # run chain trace investigation in the background.
                task = run_chain_trace.delay(trace_params)
                request.session["active_trace_task_id"] = task.id
                print("passed it to celery")

                return redirect('trace_running')
            except Exception as e:
                error_message = f"An error occurred during the investigation: {e}"

                messages.error(request, error_message)
                return redirect('investigation_setup')
        else:
            error_message = f"Form is invalid. Errors: {form.errors}"

            messages.error(request, error_message)
            return redirect('investigation_setup')

    return render(request, "core/investigation_setup.html")

def trace_running(request):
    task_id = request.session.get("active_trace_task_id")
    context = {
        "task_id" : task_id
    }
    return render(request, "core/trace_running.html", context)


def investigation_result(request):
    task_id = request.session.get("active_trace_task_id")

    if not task_id:
        messages.error(request, "No active investigation found.")
        return redirect("investigation_setup")
    
    task_result = AsyncResult(task_id)
    
    context = {
        "task_id" : task_id,
        "task_status" : task_result.status,
        "task_result" : task_result.result[1]
    }
    return render(request, "core/investigation_result.html", context)


def graph_explorer(request):
    return render(request, "core/graph_explorer.html")


def get_trace_status(request, task_id):
    task_result = AsyncResult(task_id)

    response_data = {
        "task_id": task_id,
        "status": task_result.status, # e.g. "PENDING", "SUCCESS", "FAILURE"
        "ready": task_result.ready(),
    }

    if task_result.ready():
        if task_result.successful():
            response_data["result"] = task_result.result
        else:
            response_data["error"] = str(task_result.result)

    return JsonResponse(response_data)


