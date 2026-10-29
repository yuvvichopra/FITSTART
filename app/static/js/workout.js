// Dynamic workout logger
document.addEventListener('DOMContentLoaded', function () {
    const addSetButtons = document.querySelectorAll('.btn-add-set');
    const setsContainer = document.getElementById('workout-sets-tbody');

    if (addSetButtons.length > 0 && setsContainer) {
        addSetButtons.forEach(btn => {
            btn.addEventListener('click', function () {
                const exerciseName = this.getAttribute('data-exercise');
                const rowCount = setsContainer.querySelectorAll('tr').length + 1;

                // Find highest existing set number for this exercise
                let highestSet = 0;
                setsContainer.querySelectorAll('tr').forEach(row => {
                    const exInput = row.querySelector('input[name="exercise_name[]"]');
                    const setInput = row.querySelector('input[name="set_number[]"]');
                    if (exInput && exInput.value === exerciseName && setInput) {
                        const num = parseInt(setInput.value) || 0;
                        if (num > highestSet) highestSet = num;
                    }
                });

                const newSetNum = highestSet + 1;

                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td>
                        <strong>${exerciseName}</strong>
                        <input type="hidden" name="exercise_name[]" value="${exerciseName}">
                    </td>
                    <td style="width: 80px;">
                        <input type="number" name="set_number[]" value="${newSetNum}" class="form-control" style="padding: 0.35rem;" required>
                    </td>
                    <td style="width: 110px;">
                        <input type="number" step="0.5" name="weight_kg[]" placeholder="0" class="form-control" style="padding: 0.35rem;" required>
                    </td>
                    <td style="width: 90px;">
                        <input type="number" name="reps_completed[]" placeholder="10" class="form-control" style="padding: 0.35rem;" required>
                    </td>
                    <td style="width: 90px;">
                        <input type="number" step="0.5" min="1" max="10" name="rpe[]" placeholder="7.5" class="form-control" style="padding: 0.35rem;">
                    </td>
                    <td>
                        <input type="text" name="item_notes[]" placeholder="Form cues or ease" class="form-control" style="padding: 0.35rem;">
                    </td>
                    <td style="width: 50px; text-align: center;">
                        <button type="button" class="btn btn-sm btn-danger remove-set-btn" style="padding: 0.2rem 0.5rem;">✕</button>
                    </td>
                `;
                setsContainer.appendChild(tr);

                tr.querySelector('.remove-set-btn').addEventListener('click', function () {
                    tr.remove();
                });
            });
        });
    }

    // Delegate remove button for pre-rendered rows
    document.addEventListener('click', function (e) {
        if (e.target && e.target.classList.contains('remove-set-btn')) {
            const tr = e.target.closest('tr');
            if (tr) tr.remove();
        }
    });
});
