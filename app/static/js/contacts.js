document.addEventListener("DOMContentLoaded", function () {

    console.log("JS LOADED");

    const form = document.getElementById("contactForm");
    const fullName = document.getElementById("fullName");
    const email = document.getElementById("email");
    const phone = document.getElementById("phone");
    const message = document.getElementById("message");

    form.addEventListener("submit", function (e) {
        e.preventDefault();

        let isValid = true;

        // FULL NAME
        if (fullName.value.trim() === "") {
            fullName.classList.add("is-invalid");
            isValid = false;
        } else {
            fullName.classList.remove("is-invalid");
            fullName.classList.add("is-valid");
        }

        // EMAIL
        if (email.value.trim() === "") {
            email.classList.add("is-invalid");
            isValid = false;
        } else {
            email.classList.remove("is-invalid");
            email.classList.add("is-valid");
        }

        // MESSAGE
        if (message.value.trim() === "" || message.value.length > 500) {
            message.classList.add("is-invalid");
            isValid = false;
        } else {
            message.classList.remove("is-invalid");
            message.classList.add("is-valid");
        }

        if (!isValid) return;

        // DATA TO SEND
        const msgData = [
            fullName.value.trim(),
            email.value.trim(),
            phone.value.trim(),
            message.value.trim()
        ];

        fetch("/sendMsg", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ msgData: msgData })
        })
            .then(res => {
                if (!res.ok) throw new Error("Server error");
                return res.json();
            })
            .then(data => {
                if (data.status === "success") {

                    alert("Your message has been sent successfully.");

                    form.reset();
                    charCount.textContent = "0 / 500";

                    [fullName, email, message].forEach(el => {
                        el.classList.remove("is-valid");
                    });

                    // CLOSE MODAL SAFELY
                    const modalEl = document.getElementById("contactModal");
                    const modal = bootstrap.Modal.getInstance(modalEl);
                    modal.hide();

                    modalEl.addEventListener("hidden.bs.modal", function () {
                        document.body.classList.remove("modal-open");
                        document.querySelectorAll(".modal-backdrop")
                            .forEach(b => b.remove());
                    }, { once: true });

                } else {
                    alert("An error occurred. Message could not be sent.");
                }
            })
            .catch(err => {
                console.error(err);
                alert("An error occurred. Message could not be sent.");
            });
    });
});
