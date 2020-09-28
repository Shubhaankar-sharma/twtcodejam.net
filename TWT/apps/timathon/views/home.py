from allauth.socialaccount.models import SocialAccount
from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views import View

from TWT.apps.timathon.models import Team
from TWT.context import get_discord_context
from TWT.apps.challenges.models.challenge import Challenge


class HomeView(View):
    def get_context(self, request: WSGIRequest):
        context = get_discord_context(request=request)
        challenges = Challenge.objects.all()

        context['challenges'] = \
            [challenge for challenge in challenges if challenge.type == Challenge.ChallengeType.MONTHLY]

        context['current_challenge'] = [challenge for challenge in challenges
                                        if challenge.type == Challenge.ChallengeType.MONTHLY and not challenge.ended]

        context['current_challenge'] = context['current_challenge'][0] or None
        if context['current_challenge']:
            old_teams = Team.objects.filter(challenge_id=context['current_challenge'].id)
            teams = []
            for team in old_teams:
                members = team.members.all()
                discord_members = []
                for member in members:
                    new_member = {}
                    try:
                        user = SocialAccount.objects.get(user_id=member.id)
                    except SocialAccount.DoesNotExist:
                        pass
                    else:
                        new_member["user_id"] = user.uid
                        new_member["avatar_url"] = user.get_avatar_url()
                        new_member["username"] = user.extra_data["username"]
                        new_member["discriminator"] = user.extra_data["discriminator"]
                    discord_members.append(new_member)
                team.discord_members = discord_members
                teams.append(team)

            context['teams'] = teams

        print(context)
        return context

    def get(self, request: WSGIRequest) -> HttpResponse:
        context = self.get_context(request)

        if not request.user.is_authenticated:
            return redirect()

        return render(request, template_name='timathon/index.html', context=context)