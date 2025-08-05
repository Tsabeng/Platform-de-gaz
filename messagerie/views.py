from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages as django_messages
from django.http import HttpResponseForbidden
from .models import Message
from .forms import MessageForm

@login_required
def inbox(request):
    messages = Message.objects.filter(recipient=request.user).order_by('-timestamp')
    return render(request, 'messagerie/inbox.html', {'messages': messages})

@login_required
def compose_message(request):
    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.sender = request.user
            message.save()
            return redirect('inbox')
    else:
        form = MessageForm()
    return render(request, 'messagerie/compose.html', {'form': form})



@login_required
def message_detail(request, pk):
    message = get_object_or_404(Message, pk=pk, recipient=request.user)
    if not message:
        message = get_object_or_404(Message, pk=pk, sender=request.user)
    return render(request, 'messagerie/message_detail.html', {'message': message})


@login_required
def delete_message(request, pk):
    message = get_object_or_404(Message, pk=pk, recipient=request.user)
    if request.method == 'POST':
        message.delete()
        django_messages.success(request, "Message supprimé avec succès.")
        return redirect('inbox')
    return render(request, 'messagerie/delete_confirm.html', {'message': message})
@login_required
def reply_message(request, pk):
    original_message = get_object_or_404(Message, pk=pk, recipient=request.user)

    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            reply = form.save(commit=False)
            reply.sender = request.user
            # On inverse destinataire et expéditeur
            reply.recipient = original_message.sender
            reply.save()
            django_messages.success(request, "Réponse envoyée !")
            return redirect('inbox')
    else:
        initial_data = {
            'recipient': original_message.sender,
            'subject': 'Reponse A: ' + original_message.subject if not original_message.subject.startswith('Re:') else original_message.subject,
        }
        form = MessageForm(initial=initial_data)

    return render(request, 'messagerie/compose.html', {'form': form, 'replying_to': original_message})

@login_required
def sent_messages(request):
    messages = Message.objects.filter(sender=request.user).order_by('-timestamp')
    return render(request, 'messagerie/sent_messages.html', {'messages': messages})



