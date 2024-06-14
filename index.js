const venom = require("venom-bot");
const request = require("request");
const banco = require("./src/banco");

const treinamento = `Você é um especialista em autismo, responda as perguntas que vierem sempre como um especialista nesse assunto. Para esse contexto, considere que a pessoa que está conversando com você é um pai de uma criança autista e está buscando informações sobre o assunto. Então, quando a primeira mensagem for enviada, responda com um texto dizendo que você é um especialista em autismo e que pode ajudar com informações sobre o assunto.`;

venom.create({
    session: "chatGPT_BOT",
    multidevice: true
})
.then(client => start(client))
.catch(err => console.log(err));

const header = {
    "Content-Type": "application/json",
    "Authorization": "Bearer sk-proj-v58GXoRe2lbnyCY3iyh2T3BlbkFJ15ucaKwwkPWRWJAZcMQq"
};

const start = (client) => {
    client.onMessage((message) => {
        const userCadastrado = banco.db.find(numero => numero.num === message.from);
        if (!userCadastrado) {
            console.log("Cadastrando usuário");
            banco.db.push({ num: message.from, historico: [] });
        } else {
            console.log("Usuário já cadastrado");
        }

        const historico = banco.db.find(num => num.num === message.from);
        historico.historico.push("user: " + message.body);
        console.log(historico.historico);

        console.log(banco.db);
        
        const requestData = {
            url: "https://api.openai.com/v1/chat/completions",
            method: "POST",
            headers: header,
            json: {
                model: "gpt-3.5-turbo",
                messages: [
                    { role: "system", content: treinamento },
                    { role: "system", content: "historico de conversas: " + historico.historico },
                    { role: "user", content: message.body }
                ]
            }
        };

        // Faça a solicitação POST
        request(requestData, (error, response, body) => {
            if (error) {
                console.error(error);
            } else if (response.statusCode !== 200) {
                console.error("Erro:", response.statusCode);
                console.error(body);
            } else {
                const responseContent = body.choices[0].message.content;
                console.log(responseContent);
                historico.historico.push("assistent: " + responseContent);
                client.sendText(message.from, responseContent);
            }
        });

    });
};
