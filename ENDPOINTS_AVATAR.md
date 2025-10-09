# 📸 Endpoints de Avatar

## 🎯 Funcionalidades

Gerenciamento completo de avatares (fotos de perfil) dos usuários.

---

## 📋 Endpoints Disponíveis

### **1. Upload de Avatar (Usuário Atual)**

**POST** `/avatars/upload`

Upload de avatar para o usuário logado.

**Headers:**
```json
{
  "Authorization": "Bearer {seu_token}"
}
```

**Body (form-data):**
```
file: [arquivo de imagem]
```

**Resposta de Sucesso:**
```json
{
  "message": "Avatar atualizado com sucesso",
  "avatar_url": "/static/avatars/abc123.jpg",
  "user": {
    "id": 1,
    "username": "joao",
    "full_name": "João Silva",
    "avatar_url": "/static/avatars/abc123.jpg"
  }
}
```

---

### **2. Upload de Avatar (Por ID)**

**POST** `/avatars/{user_id}/upload`

Upload de avatar para um usuário específico (Admin ou próprio usuário).

**Parâmetros:**
- `user_id` (path): ID do usuário

**Permissões:**
- ✅ Admin pode alterar de qualquer usuário
- ✅ Usuário pode alterar apenas o próprio

---

### **3. Ver Avatar (Usuário Atual)**

**GET** `/avatars/me`

Obter informações do avatar do usuário logado.

**Resposta:**
```json
{
  "user_id": 1,
  "username": "joao",
  "avatar_url": "/static/avatars/abc123.jpg",
  "file_size": 45678,
  "file_exists": true
}
```

---

### **4. Ver Avatar (Por ID)**

**GET** `/avatars/{user_id}`

Obter informações do avatar de qualquer usuário (público).

**Parâmetros:**
- `user_id` (path): ID do usuário

---

### **5. Deletar Avatar (Usuário Atual)**

**DELETE** `/avatars/me`

Deletar o avatar do usuário logado.

**Resposta:**
```json
{
  "message": "Avatar deletado com sucesso",
  "file_deleted": true,
  "user": {
    "id": 1,
    "username": "joao",
    "avatar_url": null
  }
}
```

---

### **6. Deletar Avatar (Por ID)**

**DELETE** `/avatars/{user_id}`

Deletar avatar de um usuário específico (Admin ou próprio usuário).

**Permissões:**
- ✅ Admin pode deletar de qualquer usuário
- ✅ Usuário pode deletar apenas o próprio

---

### **7. Listar Usuários com Avatares**

**GET** `/avatars/`

Listar todos os usuários com informações de avatar (Admin apenas).

**Query Params:**
- `skip` (opcional): Pular N registros (padrão: 0)
- `limit` (opcional): Limitar resultados (padrão: 100)

**Resposta:**
```json
[
  {
    "id": 1,
    "username": "admin",
    "full_name": "Administrador",
    "avatar_url": "/static/avatars/abc123.jpg",
    "has_avatar": true
  },
  {
    "id": 2,
    "username": "joao",
    "full_name": "João Silva",
    "avatar_url": null,
    "has_avatar": false
  }
]
```

---

## 📝 Regras e Validações

### **Extensões Permitidas:**
- ✅ JPG / JPEG
- ✅ PNG
- ✅ GIF
- ✅ WEBP

### **Tamanho Máximo:**
- 📦 **5 MB** por arquivo

### **Comportamento:**
- 🔄 Upload de novo avatar **substitui** o antigo automaticamente
- 🗑️ Arquivo físico é deletado ao fazer upload de novo ou deletar
- 📁 Arquivos salvos em: `static/avatars/`

---

## 🧪 Como Testar

### **1. Via Swagger UI:**
```
http://localhost:8000/docs
```
- Procure pela seção **"Avatars"**
- Use o botão **"Try it out"**
- Selecione um arquivo de imagem
- Execute!

### **2. Via cURL:**

**Upload de avatar:**
```bash
curl -X POST "http://localhost:8000/avatars/upload" \
  -H "Authorization: Bearer SEU_TOKEN" \
  -F "file=@caminho/para/foto.jpg"
```

**Ver avatar:**
```bash
curl -X GET "http://localhost:8000/avatars/me" \
  -H "Authorization: Bearer SEU_TOKEN"
```

**Deletar avatar:**
```bash
curl -X DELETE "http://localhost:8000/avatars/me" \
  -H "Authorization: Bearer SEU_TOKEN"
```

### **3. Via Frontend (JavaScript/React):**

```javascript
// Upload de avatar
const uploadAvatar = async (file) => {
  const formData = new FormData();
  formData.append('file', file);

  const response = await fetch('http://localhost:8000/avatars/upload', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`
    },
    body: formData
  });

  return await response.json();
};

// Ver avatar
const getAvatar = async () => {
  const response = await fetch('http://localhost:8000/avatars/me', {
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });

  return await response.json();
};

// Deletar avatar
const deleteAvatar = async () => {
  const response = await fetch('http://localhost:8000/avatars/me', {
    method: 'DELETE',
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });

  return await response.json();
};
```

---

## 🔐 Permissões

| Endpoint | Usuário | Admin |
|----------|---------|-------|
| POST `/avatars/upload` | ✅ Próprio | ✅ Próprio |
| POST `/avatars/{id}/upload` | ✅ Se for próprio ID | ✅ Qualquer |
| GET `/avatars/me` | ✅ Próprio | ✅ Próprio |
| GET `/avatars/{id}` | ✅ Qualquer | ✅ Qualquer |
| DELETE `/avatars/me` | ✅ Próprio | ✅ Próprio |
| DELETE `/avatars/{id}` | ✅ Se for próprio ID | ✅ Qualquer |
| GET `/avatars/` | ❌ | ✅ Apenas Admin |

---

## 🎨 Visualizar Avatar

Após upload, a URL do avatar estará disponível em:

```
http://localhost:8000/static/avatars/abc123.jpg
```

Use no `<img>` tag:
```html
<img src="http://localhost:8000/static/avatars/abc123.jpg" alt="Avatar" />
```

Ou no React:
```jsx
<img src={user.avatar_url} alt={user.full_name} />
```

---

## ❓ FAQ

**P: O que acontece com o avatar antigo ao fazer novo upload?**  
R: É automaticamente deletado (arquivo e referência no banco).

**P: Posso usar qualquer tipo de imagem?**  
R: Apenas JPG, PNG, GIF e WEBP. Máximo 5MB.

**P: O avatar é público?**  
R: A visualização da URL é pública, mas o upload/delete requer autenticação.

**P: Onde os arquivos são salvos?**  
R: Em `static/avatars/` com nome único (UUID).

