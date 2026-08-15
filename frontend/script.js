const API_URL = "http://127.0.0.1:8000";

const taskForm = document.getElementById("taskForm");
const taskList = document.getElementById("taskList");
const titleError = document.getElementById("titleError");
const taskMessage = document.getElementById("taskMessage");
const refreshButton = document.getElementById("refreshButton");


// -------------------------
// LOAD TASKS
// -------------------------

async function loadTasks() {
    try {
        const response = await fetch(`${API_URL}/tasks`);

        if (!response.ok) {
            throw new Error("Failed to load tasks");
        }

        const tasks = await response.json();

        localStorage.setItem("taskflow_tasks", JSON.stringify(tasks));

        renderTasks(tasks);

    } catch (error) {
        console.error(error);

        const cachedTasks =
            localStorage.getItem("taskflow_tasks");

        if (cachedTasks) {
            renderTasks(JSON.parse(cachedTasks));
            showMessage("Showing cached tasks.");
        } else {
            showMessage("Unable to connect to TaskFlow API.");
        }
    }
}


// -------------------------
// RENDER TASKS
// -------------------------

function renderTasks(tasks) {
    taskList.replaceChildren();

    if (tasks.length === 0) {
        const emptyMessage = document.createElement("p");
        emptyMessage.textContent = "No tasks found.";
        taskList.appendChild(emptyMessage);
        return;
    }

    tasks.forEach((task) => {
        const card = document.createElement("article");
        card.className = "task-card";

        const title = document.createElement("h3");
        title.textContent = task.title;

        const description = document.createElement("p");
        description.textContent =
            task.description || "No description";

        const priority = document.createElement("p");
        priority.textContent =
            `Priority: ${task.priority}`;

        const dueDate = document.createElement("p");
        dueDate.textContent =
            `Due: ${task.due_date || "Not set"}`;

        const status = document.createElement("p");
        status.textContent =
            `Status: ${task.status}`;

        const actions = document.createElement("div");
        actions.className = "task-actions";

        const editButton = document.createElement("button");
        editButton.textContent = "Edit";
        editButton.className = "edit-button";

        editButton.addEventListener("click", () => {
            editTask(task);
        });

        const deleteButton = document.createElement("button");
        deleteButton.textContent = "Delete";
        deleteButton.className = "delete-button";

        deleteButton.addEventListener("click", () => {
            deleteTask(task.id);
        });

        actions.appendChild(editButton);
        actions.appendChild(deleteButton);

        card.appendChild(title);
        card.appendChild(description);
        card.appendChild(priority);
        card.appendChild(dueDate);
        card.appendChild(status);
        card.appendChild(actions);

        taskList.appendChild(card);
    });
}


// -------------------------
// ADD TASK
// -------------------------

taskForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    titleError.textContent = "";
    taskMessage.textContent = "";

    const title =
        document.getElementById("title").value.trim();

    if (!title) {
        titleError.textContent =
            "Title cannot be blank.";
        return;
    }

    const description =
        document.getElementById("description").value.trim();

    const priority =
        document.getElementById("priority").value;

    const dueDate =
        document.getElementById("dueDate").value.trim();

    const projectId =
        Number(document.getElementById("projectId").value);

    const taskData = {
        title: title,
        description: description || null,
        priority: priority,
        due_date: dueDate || null,
        status: "pending",
        project_id: projectId
    };

    try {
        const response = await fetch(
            `${API_URL}/tasks`,
            {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(taskData)
            }
        );

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(
                errorData.detail || "Failed to create task"
            );
        }

        taskForm.reset();

        document.getElementById("priority").value =
            "medium";

        document.getElementById("projectId").value =
            "1";

        showMessage("Task added successfully.");

        await loadTasks();

    } catch (error) {
        console.error(error);
        showMessage(error.message);
    }
});


// -------------------------
// EDIT TASK
// -------------------------

async function editTask(task) {
    const newTitle = prompt(
        "Enter new task title:",
        task.title
    );

    if (newTitle === null) {
        return;
    }

    const title = newTitle.trim();

    if (!title) {
        showMessage("Title cannot be blank.");
        return;
    }

    const updatedTask = {
        title: title,
        description: task.description,
        priority: task.priority,
        due_date: task.due_date,
        status: task.status,
        project_id: task.project_id
    };

    try {
        const response = await fetch(
            `${API_URL}/tasks/${task.id}`,
            {
                method: "PUT",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(updatedTask)
            }
        );

        if (!response.ok) {
            throw new Error("Failed to update task");
        }

        showMessage("Task updated successfully.");

        await loadTasks();

    } catch (error) {
        console.error(error);
        showMessage(error.message);
    }
}


// -------------------------
// DELETE TASK
// -------------------------

async function deleteTask(taskId) {
    const confirmed = confirm(
        "Are you sure you want to delete this task?"
    );

    if (!confirmed) {
        return;
    }

    try {
        const response = await fetch(
            `${API_URL}/tasks/${taskId}`,
            {
                method: "DELETE"
            }
        );

        if (!response.ok) {
            throw new Error("Failed to delete task");
        }

        showMessage("Task deleted successfully.");

        await loadTasks();

    } catch (error) {
        console.error(error);
        showMessage(error.message);
    }
}


// -------------------------
// MESSAGE
// -------------------------

function showMessage(message) {
    taskMessage.textContent = message;
}


// -------------------------
// REFRESH
// -------------------------

refreshButton.addEventListener(
    "click",
    loadTasks
);


// -------------------------
// INITIAL LOAD
// -------------------------

loadTasks();