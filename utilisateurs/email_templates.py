"""Email templates for user authentication"""

def password_reset_email_html(user_email, reset_url, user_name):
    """Generate HTML email for password reset"""
    return f"""
    <!DOCTYPE html>
    <html lang="fr">
    <head>
        <meta charset="UTF-8">
        <style>
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                line-height: 1.6;
                color: #333;
            }}
            .email-container {{
                max-width: 600px;
                margin: 0 auto;
                background: #f9fafb;
                border-radius: 8px;
                overflow: hidden;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }}
            .header {{
                background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
                color: white;
                padding: 30px 20px;
                text-align: center;
            }}
            .header h1 {{
                margin: 0;
                font-size: 28px;
            }}
            .content {{
                padding: 40px 30px;
            }}
            .greeting {{
                font-size: 18px;
                margin-bottom: 20px;
            }}
            .message {{
                font-size: 14px;
                color: #555;
                margin-bottom: 30px;
                line-height: 1.8;
            }}
            .reset-button {{
                display: inline-block;
                background: #2563eb;
                color: white;
                padding: 12px 30px;
                border-radius: 6px;
                text-decoration: none;
                font-weight: bold;
                margin: 20px 0;
            }}
            .reset-button:hover {{
                background: #1d4ed8;
            }}
            .warning {{
                background: #fef3c7;
                border-left: 4px solid #f59e0b;
                padding: 15px;
                margin: 20px 0;
                border-radius: 4px;
                font-size: 13px;
                color: #92400e;
            }}
            .footer {{
                background: #f3f4f6;
                padding: 20px;
                text-align: center;
                font-size: 12px;
                color: #666;
                border-top: 1px solid #e5e7eb;
            }}
            .footer a {{
                color: #2563eb;
                text-decoration: none;
            }}
        </style>
    </head>
    <body>
        <div class="email-container">
            <div class="header">
                <h1>🚗 MOVENOW</h1>
                <p>Réinitialisation de mot de passe</p>
            </div>
            
            <div class="content">
                <div class="greeting">Bonjour {user_name},</div>
                
                <div class="message">
                    Nous avons reçu une demande de réinitialisation de mot de passe pour votre compte MOVENOW.
                    Si vous n'avez pas fait cette demande, vous pouvez ignorer cet email.
                </div>
                
                <div style="text-align: center;">
                    <a href="{reset_url}" class="reset-button">Réinitialiser mon mot de passe</a>
                </div>
                
                <div class="message" style="text-align: center; font-size: 12px; margin-top: 20px; color: #999;">
                    Ou collez ce lien dans votre navigateur:<br>
                    <code style="background: #f0f0f0; padding: 8px; display: inline-block; margin-top: 10px; border-radius: 4px;">
                        {reset_url}
                    </code>
                </div>
                
                <div class="warning">
                    ⚠️ <strong>Important:</strong> Ce lien est valable pendant 24 heures. Après expiration, 
                    vous devrez demander un nouveau lien de réinitialisation.
                </div>
                
                <div class="message" style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #e5e7eb;">
                    Si vous avez besoin d'aide, contactez notre support:<br>
                    <a href="mailto:support@movenow.com" style="color: #2563eb;">support@movenow.com</a>
                </div>
            </div>
            
            <div class="footer">
                <p>© 2026 MOVENOW - Plateforme de transport collaborative</p>
                <p>
                    <a href="https://movenow.com">Site Web</a> | 
                    <a href="https://movenow.com/contact">Contact</a> | 
                    <a href="https://movenow.com/privacy">Politique de confidentialité</a>
                </p>
            </div>
        </div>
    </body>
    </html>
    """


def welcome_email_html(user_name, user_email):
    """Generate HTML welcome email for new users"""
    return f"""
    <!DOCTYPE html>
    <html lang="fr">
    <head>
        <meta charset="UTF-8">
        <style>
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                line-height: 1.6;
                color: #333;
            }}
            .email-container {{
                max-width: 600px;
                margin: 0 auto;
                background: #f9fafb;
                border-radius: 8px;
                overflow: hidden;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }}
            .header {{
                background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
                color: white;
                padding: 30px 20px;
                text-align: center;
            }}
            .header h1 {{
                margin: 0;
                font-size: 28px;
            }}
            .content {{
                padding: 40px 30px;
            }}
            .greeting {{
                font-size: 18px;
                margin-bottom: 20px;
            }}
            .features {{
                margin: 30px 0;
            }}
            .feature {{
                display: flex;
                margin: 15px 0;
                padding: 10px;
                background: #f0f9ff;
                border-radius: 4px;
            }}
            .feature-icon {{
                font-size: 20px;
                margin-right: 15px;
            }}
            .feature-text {{
                flex: 1;
            }}
            .cta-button {{
                display: inline-block;
                background: #2563eb;
                color: white;
                padding: 12px 30px;
                border-radius: 6px;
                text-decoration: none;
                font-weight: bold;
                margin: 20px 0;
            }}
            .footer {{
                background: #f3f4f6;
                padding: 20px;
                text-align: center;
                font-size: 12px;
                color: #666;
                border-top: 1px solid #e5e7eb;
            }}
        </style>
    </head>
    <body>
        <div class="email-container">
            <div class="header">
                <h1>🚗 MOVENOW</h1>
                <p>Bienvenue!</p>
            </div>
            
            <div class="content">
                <div class="greeting">Bienvenue {user_name}!</div>
                
                <p>Merci de vous être inscrit sur MOVENOW. Nous sommes heureux de vous accueillir!</p>
                
                <div class="features">
                    <div class="feature">
                        <div class="feature-icon">📦</div>
                        <div class="feature-text">
                            <strong>Créer des commandes</strong><br>
                            Créez vos premières commandes de transport
                        </div>
                    </div>
                    <div class="feature">
                        <div class="feature-icon">💰</div>
                        <div class="feature-text">
                            <strong>Accumuler des MoveCoins</strong><br>
                            Gagnez des points à chaque trajet
                        </div>
                    </div>
                    <div class="feature">
                        <div class="feature-icon">🎁</div>
                        <div class="feature-text">
                            <strong>Obtenir des réductions</strong><br>
                            Utilisez les promotions exclusives
                        </div>
                    </div>
                </div>
                
                <div style="text-align: center;">
                    <a href="http://localhost:8000/" class="cta-button">Commencer maintenant</a>
                </div>
            </div>
            
            <div class="footer">
                <p>© 2026 MOVENOW - Plateforme de transport collaborative</p>
            </div>
        </div>
    </body>
    </html>
    """
