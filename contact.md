---
layout: page
hero_image: /assets/images/koyasan.png
hero_darken: true
title: Contact Joe Larabell
custom_css: form
permalink: /contact/
---
<form id="form-id" class="form-class" method="post" action="/contact/contact.cgi/larabell">
    <!-- This entire "form" block will be replaced by the script-generated reply -->

    <blockquote>
    This is an experimental contact page that probably doesn't work.
    </blockquote>

    <h3>Contact us:</h3>

    <div class="form-group">
        <label for="Name" class="label">Your name</label>
        <div class="input-group">
            <input type="text" id="Name" name="Name" class="form-control" required>
        </div>
    </div>

    <div class="form-group">
        <label for="Email" class="label">Your email address</label>
        <div class="input-group">
            <input type="email" id="Email" name="Email" class="form-control" required>
        </div>
    </div>

    <div class="form-group">
        <label for="Subject" class="label">I would like to:</label>
        <div class="input-group">
             <select id="Subject" name="Subject" class="form-control">
             <option value="Default">(*** Choose One ***)</option>
             <option value="Complain">complain about something on your page.</option>
             <option value="Kudos">compliment you on your flawless thinking.</option>
             <option value="Question">humbly ask you an insignificant question.</option>
             <option value="Assist">kindly offer my assistance in your quest.</option>
             <option value="Brag">let you know about my own web page(s).</option>
             <option value="Other">give you a (small) piece of my mind.</option>
             </select>
        </div>
    </div>

    <div class="form-group">
        <label for="Message" class="label">Your message</label>
        <div class="input-group">
            <textarea id="Message" name="Message" class="form-control" rows="6" maxlength="3000"></textarea>
        </div>
    </div>

    <div class="form-group">
        <button type="submit" id="button" class="btn btn-primary btn-lg btn-block">Send</button>
    </div>

    <input type="hidden" name="FormURL" value="{{ page.url }}">
</form>
