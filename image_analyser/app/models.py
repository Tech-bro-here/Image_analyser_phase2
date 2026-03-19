from django.db import models
import json


class PosterConcept(models.Model):
    user_request     = models.TextField()
    poster_title     = models.CharField(max_length=300)
    colour_theme     = models.TextField()   # JSON
    visual_elements  = models.TextField()   # JSON list
    layout_structure = models.TextField()   # JSON
    typography       = models.TextField()   # JSON
    ai_prompt        = models.TextField()   # Midjourney prompt (main)
    platform_trends  = models.TextField()   # JSON
    created_at       = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def get_colour_theme(self):
        try: return json.loads(self.colour_theme)
        except: return {}

    def get_visual_elements(self):
        try: return json.loads(self.visual_elements)
        except: return []

    def get_layout_structure(self):
        try: return json.loads(self.layout_structure)
        except: return {}

    def get_typography(self):
        try: return json.loads(self.typography)
        except: return {}

    def get_platform_trends(self):
        try: return json.loads(self.platform_trends)
        except: return {}

    def __str__(self):
        return f"{self.poster_title} ({self.created_at.strftime('%Y-%m-%d')})"