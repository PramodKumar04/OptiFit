# views.py
from django.shortcuts import render, redirect
from .forms import UserProfileForm
from django.http import HttpResponse
from django.contrib import messages
import json

def submit_user_profile(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST)
        if form.is_valid():
            # Save the user profile data
            user_profile = form.save(commit=False)
            height_in_meters = user_profile.height / 100  # Convert height to meters
            user_profile.bmi = round(user_profile.weight / (height_in_meters ** 2), 2)
            user_profile.save()

            # Save user data to a JSON file
            user_data = {
                "name": user_profile.name,
                "age": user_profile.age,
                "gender": user_profile.gender,
                "height": user_profile.height,
                "weight": user_profile.weight,
                "fitness_goal": user_profile.fitness_goal,
                "bmi": user_profile.bmi
            }

            # Save the data to a JSON file
            with open('user_profiles.json', 'a') as json_file:
                json.dump(user_data, json_file)
                json_file.write('\n')  # Write each user profile on a new line

            messages.success(request, f"Your profile has been submitted successfully. Your BMI is: {user_profile.bmi}")
            return redirect('home')
        else:
            messages.error(request, "There was an error with the form.")
    else:
        form = UserProfileForm()

    return render(request, 'submit_user_profile.html', {'form': form})
