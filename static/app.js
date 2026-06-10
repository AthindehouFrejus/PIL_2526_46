// ===== API BASE URL =====
const API_URL = 'https://web-production-903ce.up.railway.app';

// ===== STEPS NAVIGATION =====
let currentStep = 1;

function showStep(step) {
    // Masquer tous les panels
    document.querySelectorAll('.reg-panel').forEach(p => p.classList.remove('active'));
    // Afficher le bon
    document.getElementById('reg-step-' + step).classList.add('active');
    // Mettre à jour les dots
    document.querySelectorAll('.reg-step').forEach(d => d.classList.remove('active'));
    document.getElementById('step-dot-' + step).classList.add('active');
    currentStep = step;
}

function nextStep(step) {
    // Validation basique
    if (currentStep === 1) {
        const prenom = document.getElementById('reg-prenom').value.trim();
        const nom = document.getElementById('reg-nom').value.trim();
        const email = document.getElementById('reg-email').value.trim();
        const tel = document.getElementById('reg-tel').value.trim();
        if (!prenom || !nom || !email || !tel) {
            showMsg('Veuillez remplir tous les champs obligatoires.', 'error');
            return;
        }
        if (!email.includes('@')) {
            showMsg('Adresse email invalide.', 'error');
            return;
        }
    }
    showStep(step);
    hideMsg();
}

function prevStep(step) {
    showStep(step);
    hideMsg();
}

// ===== TAGS =====
const strengthsTags = [];
const weaknessesTags = [];

function addTag(event, type) {
    if (event.key === 'Enter') {
        event.preventDefault();
        const fieldId = type === 'strengths' ? 'strengths-field' : 'weaknesses-field';
        const listId = type === 'strengths' ? 'strengths-tags' : 'weaknesses-tags';
        const arr = type === 'strengths' ? strengthsTags : weaknessesTags;
        const input = document.getElementById(fieldId);
        const value = input.value.trim();

        if (value && !arr.includes(value)) {
            arr.push(value);
            renderTags(listId, arr, type);
        }
        input.value = '';
    }
}

function removeTag(value, type) {
    const arr = type === 'strengths' ? strengthsTags : weaknessesTags;
    const listId = type === 'strengths' ? 'strengths-tags' : 'weaknesses-tags';
    const index = arr.indexOf(value);
    if (index > -1) {
        arr.splice(index, 1);
        renderTags(listId, arr, type);
    }
}

function renderTags(listId, arr, type) {
    const list = document.getElementById(listId);
    list.innerHTML = arr.map(tag =>
        `<span class="badge-tag">${tag} <span class="remove-tag" onclick="removeTag('${tag}','${type}')">×</span></span>`
    ).join('');
}

// ===== PASSWORD TOGGLE =====
function togglePwd(inputId, btn) {
    const input = document.getElementById(inputId);
    const icon = btn.querySelector('i');
    if (input.type === 'password') {
        input.type = 'text';
        icon.classList.remove('fa-eye');
        icon.classList.add('fa-eye-slash');
    } else {
        input.type = 'password';
        icon.classList.remove('fa-eye-slash');
        icon.classList.add('fa-eye');
    }
}

// ===== MESSAGES =====
function showMsg(text, type) {
    const msg = document.getElementById('regMsg');
    msg.textContent = text;
    msg.className = 'form-msg ' + type;
    msg.style.display = 'block';
}

function hideMsg() {
    document.getElementById('regMsg').style.display = 'none';
}

// ===== REGISTER =====
async function handleRegister() {
    // Récupérer toutes les valeurs
    const prenom = document.getElementById('reg-prenom').value.trim();
    const nom = document.getElementById('reg-nom').value.trim();
    const email = document.getElementById('reg-email').value.trim();
    const tel = document.getElementById('reg-tel').value.trim();
    const filiere = document.getElementById('reg-filiere').value;
    const niveau = document.getElementById('reg-niveau').value;
    const pwd = document.getElementById('reg-pwd').value;
    const pwd2 = document.getElementById('reg-pwd2').value;
    const bio = document.getElementById('reg-bio').value.trim();

    // Récupérer disponibilités cochées
    const dispoCheckboxes = document.querySelectorAll('.dispo-item input:checked');
    const disponibilites = Array.from(dispoCheckboxes).map(cb => cb.value);

    // Validation
    if (!prenom || !nom || !email || !tel) {
        showMsg('Veuillez remplir tous les champs obligatoires.', 'error');
        return;
    }
    if (pwd !== pwd2) {
        showMsg('Les mots de passe ne correspondent pas.', 'error');
        return;
    }
    if (pwd.length < 6) {
        showMsg('Le mot de passe doit contenir au moins 6 caractères.', 'error');
        return;
    }

    // Construire l'objet pour l'API
    const body = {
        email: email,
        phone: tel,
        password: pwd,
        first_name: prenom,
        last_name: nom,
        competences: strengthsTags,
        lacunes: weaknessesTags
    };

    try {
        showMsg('Création du compte en cours...', 'success');
        const response = await fetch(API_URL + '/api/auth/register', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(body)
        });

        const data = await response.json();

        if (response.ok) {
            // Mettre à jour le profil avec les infos supplémentaires
            const token = localStorage.getItem('token'); // Pas encore de token ici
            showMsg('Compte créé avec succès ! Redirection...', 'success');
            setTimeout(() => {
                window.location.href = 'login.html';
            }, 1500);
        } else {
            showMsg(data.error || 'Erreur lors de l\'inscription.', 'error');
        }
    } catch (error) {
        showMsg('Erreur de connexion au serveur.', 'error');
        console.error(error);
    }
}
