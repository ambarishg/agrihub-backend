def create_body(URL):
    # HTML content for the email body using tables for better compatibility
    body = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
    </head>
    <body style="margin: 0; padding: 0;">
        <table width="100%" cellpadding="0" cellspacing="0" style="background-color: #F2F2F2;">
            <tr>
                <td align="center">
                    <table width="600" cellpadding="0" cellspacing="0" style="background-color: white; border-radius: 8px; overflow: hidden;">
                        <tr>
                            <td style="padding: 20px;">
                                <h1>Welcome to the Buzzing Community!</h1>
                                <p>Dear Bee Lover,</p>
                                <p>Please reset your password by clicking the button below:</p>
                                <a href={URL} style="background-color: #FFD700; color: black; padding: 15px 32px; text-align: center; text-decoration: none; display: inline-block; font-size: 16px; margin: 4px 2px; cursor: pointer; border-radius: 12px;">Explore Now</a> <!-- Replace with your URL -->
                                <p>Happy buzzing!</p>
                                <p>Best regards,<br>Bee Well</p>
                            </td>
                        </tr>
                    </table>
                </td>
            </tr>
        </table>
    </body>
    </html>
    """

    return(body)
