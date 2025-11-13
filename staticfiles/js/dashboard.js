(function () {
    const timeNowEl = document.getElementById("timeNow");
    const dateNowEl = document.getElementById("dateNow");
    const errorBox = document.getElementById("errorBox");
    const scheduleMeta = document.getElementById("scheduleMeta");
    const tableBody = document.getElementById("tableBody");
    const currentBox = document.getElementById("currentBox");
    const currentNameEl = document.getElementById("currentName");
    const countdownEl = document.getElementById("countdown");
    const nextPeriodEl = document.getElementById("nextPeriod");
    const noPeriodEl = document.getElementById("noPeriod");

    let periods = [];

    function pad(n) {
        return n.toString().padStart(2, "0");
    }

    function formatTime(date) {
        return pad(date.getHours()) + ":" + pad(date.getMinutes()) + ":" + pad(date.getSeconds());
    }

    function formatDate(date) {
        const days = ["الأحد","الاثنين","الثلاثاء","الأربعاء","الخميس","الجمعة","السبت"];
        const months = ["يناير","فبراير","مارس","أبريل","مايو","يونيو","يوليو","أغسطس","سبتمبر","أكتوبر","نوفمبر","ديسمبر"];
        return (
            days[date.getDay()] +
            " - " +
            date.getDate() +
            " " +
            months[date.getMonth()] +
            " " +
            date.getFullYear()
        );
    }

    function typeLabel(type) {
        switch (type) {
            case "start": return "بداية الدوام";
            case "class": return "حصة دراسية";
            case "break": return "فسحة / استراحة";
            case "end": return "نهاية الدوام";
            default: return "فترة";
        }
    }

    function typeClass(type) {
        switch (type) {
            case "start": return "tag tag-start";
            case "class": return "tag tag-class";
            case "break": return "tag tag-break";
            case "end": return "tag tag-end";
            default: return "tag";
        }
    }

    async function loadSchedule() {
        try {
            const res = await fetch("/timetable/api/today-schedule/");
            const data = await res.json();

            if (!data.success) {
                // لا يوجد جدول لليوم
                scheduleMeta.textContent = data.message || "لا يوجد جدول لهذا اليوم.";
                tableBody.innerHTML = "";
                periods = [];

                // إظهار رسالة عدم وجود فترة
                currentBox.classList.add("hidden");
                noPeriodEl.classList.remove("hidden");

                // إخفاء صندوق الأخطاء
                errorBox.classList.add("hidden");
                errorBox.textContent = "";

                return;
            }

            // يوجد جدول
            periods = data.periods || [];
            scheduleMeta.textContent =
                "تاريخ اليوم: " + data.date + " – جدول: " + data.schedule_name;

            errorBox.classList.add("hidden");
            errorBox.textContent = "";

            renderTable();
        } catch (e) {
            // خطأ اتصال بالسيرفر
            errorBox.textContent = "فشل الاتصال بالخادم.";
            errorBox.classList.remove("hidden");
        }
    }

    function renderTable() {
        tableBody.innerHTML = "";

        if (!periods.length) {
            const tr = document.createElement("tr");
            const td = document.createElement("td");
            td.colSpan = 5;
            td.className = "table-placeholder";
            td.textContent = "لا يوجد جدول مفعّل لهذا اليوم.";
            tr.appendChild(td);
            tableBody.appendChild(tr);
            return;
        }

        const now = new Date();

        periods.forEach((p) => {
            const start = new Date(p.start);
            const end = new Date(p.end);

            let rowClass = "";
            let statusClass = "";
            let statusTitle = "";

            if (now > end) {
                rowClass = "row-finished";
                statusClass = "status-dot status-done";
                statusTitle = "انتهت";
            } else if (now >= start && now <= end) {
                rowClass = "row-current";
                statusClass = "status-dot status-running";
                statusTitle = "جارية الآن";
            } else {
                statusClass = "status-dot status-upcoming";
                statusTitle = "قادمة";
            }

            const tr = document.createElement("tr");
            if (rowClass) tr.className = rowClass;

            const tdStatus = document.createElement("td");
            const dot = document.createElement("span");
            dot.className = statusClass;
            dot.title = statusTitle;
            tdStatus.appendChild(dot);

            const tdName = document.createElement("td");
            tdName.textContent = p.name;

            const tdType = document.createElement("td");
            const spanType = document.createElement("span");
            spanType.className = typeClass(p.type);
            spanType.textContent = typeLabel(p.type);
            tdType.appendChild(spanType);

            const tdStart = document.createElement("td");
            tdStart.textContent = start.toLocaleTimeString("ar-SA", {
                hour: "2-digit",
                minute: "2-digit",
            });

            const tdEnd = document.createElement("td");
            tdEnd.textContent = end.toLocaleTimeString("ar-SA", {
                hour: "2-digit",
                minute: "2-digit",
            });

            tr.appendChild(tdStatus);
            tr.appendChild(tdName);
            tr.appendChild(tdType);
            tr.appendChild(tdStart);
            tr.appendChild(tdEnd);

            tableBody.appendChild(tr);
        });
    }

    function updateClockAndState() {
        const now = new Date();
        timeNowEl.textContent = formatTime(now);
        dateNowEl.textContent = formatDate(now);

        if (!periods.length) {
            // لا يوجد جدول: إخفاء الفترة الحالية، إظهار "لا توجد فترة"
            currentBox.classList.add("hidden");
            noPeriodEl.classList.remove("hidden");
            countdownEl.textContent = "";
            nextPeriodEl.textContent = "";
            return;
        }

        let current = null;
        let currentIndex = -1;

        periods.forEach((p, idx) => {
            const start = new Date(p.start);
            const end = new Date(p.end);
            if (now >= start && now <= end) {
                current = p;
                currentIndex = idx;
            }
        });

        if (!current) {
            // لا توجد فترة جارية الآن
            currentBox.classList.add("hidden");
            noPeriodEl.classList.remove("hidden");
            countdownEl.textContent = "";
            nextPeriodEl.textContent = "";
        } else {
            // يوجد فترة جارية
            currentBox.classList.remove("hidden");
            noPeriodEl.classList.add("hidden");

            currentNameEl.textContent =
                current.name + " (" + typeLabel(current.type) + ")";

            const end = new Date(current.end);
            let diffSec = Math.max(0, Math.floor((end - now) / 1000));
            const m = Math.floor(diffSec / 60);
            const s = diffSec % 60;
            countdownEl.textContent =
                "الوقت المتبقي: " + pad(m) + ":" + pad(s);

            const next = periods[currentIndex + 1];
            if (next) {
                const ns = new Date(next.start);
                nextPeriodEl.textContent =
                    "الفترة القادمة: " +
                    next.name +
                    " (" +
                    typeLabel(next.type) +
                    ") – " +
                    ns.toLocaleTimeString("ar-SA", {
                        hour: "2-digit",
                        minute: "2-digit",
                    });
            } else {
                nextPeriodEl.textContent =
                    "لا توجد فترة أخرى بعد هذه الفترة.";
            }
        }

        // تحديث الحالات اللونية في الجدول
        renderTable();
    }

    // تشغيل أولي
    loadSchedule();
    updateClockAndState();

    // تحديث الساعة والحالة كل ثانية
    setInterval(updateClockAndState, 1000);

    // تحديث الجدول من الـ API كل 5 دقائق
    setInterval(loadSchedule, 5 * 60 * 1000);
})();
