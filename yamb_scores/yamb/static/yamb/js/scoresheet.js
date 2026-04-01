// Yamb Scoresheet JavaScript
// Handles dynamic form management and automatic score calculations

document.addEventListener('DOMContentLoaded', function() {
  const container = document.getElementById('scoresheet-container');
  const totalFormsInput = document.getElementById('id_yamb_scoresheets-TOTAL_FORMS');
  const addBtn = document.getElementById('add-scoresheet');
  
  if (!container || !totalFormsInput || !addBtn) {
    return; // Not on the scoresheet form page
  }
  
  // Populate the initial form's player select with all options from data attribute
  const playersData = container?.getAttribute('data-player-options');
  if (playersData) {
    try {
      const players = JSON.parse(playersData);
      const firstPlayerSelect = document.querySelector('#id_yamb_scoresheets-0-player');
      if (firstPlayerSelect) {
        // Get current value to preserve selection
        const currentValue = firstPlayerSelect.value;
        // Clear and rebuild options
        firstPlayerSelect.innerHTML = '<option value="">-- Select a player --</option>' +
          players.map(p => `<option value="${p.id}">${p.name}</option>`).join('');
        // Restore selection if it exists
        if (currentValue) {
          firstPlayerSelect.value = currentValue;
        }
      }
    } catch (e) {
      console.error('Failed to populate initial player select:', e);
    }
  }
  
  // Get player select options HTML from data attribute or first form
  function getPlayerSelectHTML(formCount) {
    let playerOptionsHTML = '';
    
    // First try to get players from data attribute
    const containerElement = document.getElementById('scoresheet-container');
    const playersData = containerElement?.getAttribute('data-player-options');
    
    if (playersData) {
      try {
        const players = JSON.parse(playersData);
        playerOptionsHTML = players
          .map(player => `<option value="${player.id}">${player.name}</option>`)
          .join('');
      } catch (e) {
        console.error('Failed to parse player data:', e);
      }
    } else {
      // Fallback: try to get from existing select on page
      const firstPlayerSelect = document.querySelector('#id_yamb_scoresheets-0-player');
      if (firstPlayerSelect) {
        playerOptionsHTML = Array.from(firstPlayerSelect.options)
          .filter(option => option.value !== '') // Exclude empty option from fallback
          .map(option => `<option value="${option.value}">${option.text}</option>`)
          .join('');
      }
    }
    
    // Always include empty option first
    const optionsHTML = `<option value="">-- Select a player --</option>${playerOptionsHTML}`;
    
    return `<select name="yamb_scoresheets-${formCount}-player" id="id_yamb_scoresheets-${formCount}-player" class="form-control">${optionsHTML}</select>`;
  }
  
  // Template for a new scoresheet
  function createNewScoresheet(formCount) {
    const playerSelectHTML = getPlayerSelectHTML(formCount);
    const template = `
      <div class="scoresheet-wrapper" style="margin-bottom: 3rem; padding-bottom: 2rem; border-bottom: 2px solid #ddd; position: relative;">
        <button type="button" class="remove-scoresheet" style="position: absolute; top: 0; right: 0; background: #dc3545; color: white; border: none; border-radius: 4px; width: 32px; height: 32px; cursor: pointer; font-size: 20px; line-height: 1; padding: 0;">&times;</button>
        <h3>Player: ${playerSelectHTML}</h3>
        
        <div class="row-1-error" style="display: none; color: #c33; background: #fee; border: 1px solid #c33; padding: 0.5rem; margin: 0.5rem 0; border-radius: 4px; font-size: 0.9rem;"></div>
        <div class="row-2-error" style="display: none; color: #c33; background: #fee; border: 1px solid #c33; padding: 0.5rem; margin: 0.5rem 0; border-radius: 4px; font-size: 0.9rem;"></div>
        <div class="row-3-error" style="display: none; color: #c33; background: #fee; border: 1px solid #c33; padding: 0.5rem; margin: 0.5rem 0; border-radius: 4px; font-size: 0.9rem;"></div>
        <div class="row-4-error" style="display: none; color: #c33; background: #fee; border: 1px solid #c33; padding: 0.5rem; margin: 0.5rem 0; border-radius: 4px; font-size: 0.9rem;"></div>
        <div class="row-5-error" style="display: none; color: #c33; background: #fee; border: 1px solid #c33; padding: 0.5rem; margin: 0.5rem 0; border-radius: 4px; font-size: 0.9rem;"></div>
        <div class="row-6-error" style="display: none; color: #c33; background: #fee; border: 1px solid #c33; padding: 0.5rem; margin: 0.5rem 0; border-radius: 4px; font-size: 0.9rem;"></div>
        <div class="row-h-error" style="display: none; color: #c33; background: #fee; border: 1px solid #c33; padding: 0.5rem; margin: 0.5rem 0; border-radius: 4px; font-size: 0.9rem;"></div>
        <div class="row-l-error" style="display: none; color: #c33; background: #fee; border: 1px solid #c33; padding: 0.5rem; margin: 0.5rem 0; border-radius: 4px; font-size: 0.9rem;"></div>
        <div class="row-fh-error" style="display: none; color: #c33; background: #fee; border: 1px solid #c33; padding: 0.5rem; margin: 0.5rem 0; border-radius: 4px; font-size: 0.9rem;"></div>
        <div class="row-c-error" style="display: none; color: #c33; background: #fee; border: 1px solid #c33; padding: 0.5rem; margin: 0.5rem 0; border-radius: 4px; font-size: 0.9rem;"></div>
        <div class="row-s-error" style="display: none; color: #c33; background: #fee; border: 1px solid #c33; padding: 0.5rem; margin: 0.5rem 0; border-radius: 4px; font-size: 0.9rem;"></div>
        <div class="row-p-error" style="display: none; color: #c33; background: #fee; border: 1px solid #c33; padding: 0.5rem; margin: 0.5rem 0; border-radius: 4px; font-size: 0.9rem;"></div>
        
        <div class="scoresheet-container">
          <table class="yamb-scoresheet">
            <thead>
              <tr>
                <th>Row</th>
                <th>↓</th>
                <th>↑</th>
                <th>L</th>
                <th>S</th>
                <th>Total</th>
              </tr>
            </thead>
            <tbody>
              <tr><td><strong>1</strong></td>
                <td><input type="text" name="yamb_scoresheets-${formCount}-row_1_down" class="score-input" inputmode="numeric"></td>
                <td><input type="text" name="yamb_scoresheets-${formCount}-row_1_up" class="score-input" inputmode="numeric"></td>
                <td><input type="text" name="yamb_scoresheets-${formCount}-row_1_l" class="score-input" inputmode="numeric"></td>
                <td><input type="text" name="yamb_scoresheets-${formCount}-row_1_s" class="score-input" inputmode="numeric"></td>
                <td><input type="text" name="yamb_scoresheets-${formCount}-row_1_total" class="score-input" inputmode="numeric" readonly></td>
              </tr>
              <tr><td><strong>2</strong></td>
                <td><input type="text" name="yamb_scoresheets-${formCount}-row_2_down" class="score-input" inputmode="numeric"></td>
                <td><input type="text" name="yamb_scoresheets-${formCount}-row_2_up" class="score-input" inputmode="numeric"></td>
                <td><input type="text" name="yamb_scoresheets-${formCount}-row_2_l" class="score-input" inputmode="numeric"></td>
                <td><input type="text" name="yamb_scoresheets-${formCount}-row_2_s" class="score-input" inputmode="numeric"></td>
                  <td><input type="text" name="yamb_scoresheets-${formCount}-row_2_total" class="score-input" inputmode="numeric" readonly></td>
              </tr>
              <tr><td><strong>3</strong></td>
                <td><input type="text" name="yamb_scoresheets-${formCount}-row_3_down" class="score-input" inputmode="numeric"></td>
                <td><input type="text" name="yamb_scoresheets-${formCount}-row_3_up" class="score-input" inputmode="numeric"></td>
                <td><input type="text" name="yamb_scoresheets-${formCount}-row_3_l" class="score-input" inputmode="numeric"></td>
                <td><input type="text" name="yamb_scoresheets-${formCount}-row_3_s" class="score-input" inputmode="numeric"></td>
                <td><input type="text" name="yamb_scoresheets-${formCount}-row_3_total" class="score-input" inputmode="numeric" readonly></td>
              </tr>
              <tr><td><strong>4</strong></td>
                <td><input type="text" name="yamb_scoresheets-${formCount}-row_4_down" class="score-input" inputmode="numeric"></td>
                <td><input type="text" name="yamb_scoresheets-${formCount}-row_4_up" class="score-input" inputmode="numeric"></td>
                <td><input type="text" name="yamb_scoresheets-${formCount}-row_4_l" class="score-input" inputmode="numeric"></td>
                <td><input type="text" name="yamb_scoresheets-${formCount}-row_4_s" class="score-input" inputmode="numeric"></td>
                <td><input type="text" name="yamb_scoresheets-${formCount}-row_4_total" class="score-input" inputmode="numeric" readonly></td>
              </tr>
              <tr><td><strong>5</strong></td>
                <td><input type="text" name="yamb_scoresheets-${formCount}-row_5_down" class="score-input" inputmode="numeric"></td>
                <td><input type="text" name="yamb_scoresheets-${formCount}-row_5_up" class="score-input" inputmode="numeric"></td>
                <td><input type="text" name="yamb_scoresheets-${formCount}-row_5_l" class="score-input" inputmode="numeric"></td>
                <td><input type="text" name="yamb_scoresheets-${formCount}-row_5_s" class="score-input" inputmode="numeric"></td>
                <td><input type="text" name="yamb_scoresheets-${formCount}-row_5_total" class="score-input" inputmode="numeric" readonly></td>
              </tr>
              <tr><td><strong>6</strong></td>
                <td><input type="text" name="yamb_scoresheets-${formCount}-row_6_down" class="score-input" inputmode="numeric"></td>
                <td><input type="text" name="yamb_scoresheets-${formCount}-row_6_up" class="score-input" inputmode="numeric"></td>
                <td><input type="text" name="yamb_scoresheets-${formCount}-row_6_l" class="score-input" inputmode="numeric"></td>
                <td><input type="text" name="yamb_scoresheets-${formCount}-row_6_s" class="score-input" inputmode="numeric"></td>
                <td><input type="text" name="yamb_scoresheets-${formCount}-row_6_total" class="score-input" inputmode="numeric" readonly></td>
              </tr>
              <tr><td><strong>H</strong></td>
                <td><input type="text" name="yamb_scoresheets-${formCount}-row_h_down" class="score-input" inputmode="numeric"></td>
                <td><input type="text" name="yamb_scoresheets-${formCount}-row_h_up" class="score-input" inputmode="numeric"></td>
                <td><input type="text" name="yamb_scoresheets-${formCount}-row_h_l" class="score-input" inputmode="numeric"></td>
                <td><input type="text" name="yamb_scoresheets-${formCount}-row_h_s" class="score-input" inputmode="numeric"></td>
                <td><input type="text" name="yamb_scoresheets-${formCount}-row_h_total" class="score-input" inputmode="numeric" readonly></td>
              </tr>
              <tr><td><strong>L</strong></td>
                <td><input type="text" name="yamb_scoresheets-${formCount}-row_l_down" class="score-input" inputmode="numeric"></td>
                <td><input type="text" name="yamb_scoresheets-${formCount}-row_l_up" class="score-input" inputmode="numeric"></td>
                <td><input type="text" name="yamb_scoresheets-${formCount}-row_l_l" class="score-input" inputmode="numeric"></td>
                <td><input type="text" name="yamb_scoresheets-${formCount}-row_l_s" class="score-input" inputmode="numeric"></td>
                <td><input type="text" name="yamb_scoresheets-${formCount}-row_l_total" class="score-input" inputmode="numeric" readonly></td>
              </tr>
              <tr><td><strong>FH</strong></td>
                <td><input type="text" name="yamb_scoresheets-${formCount}-row_fh_down" class="score-input" inputmode="numeric"></td>
                <td><input type="text" name="yamb_scoresheets-${formCount}-row_fh_up" class="score-input" inputmode="numeric"></td>
                <td><input type="text" name="yamb_scoresheets-${formCount}-row_fh_l" class="score-input" inputmode="numeric"></td>
                <td><input type="text" name="yamb_scoresheets-${formCount}-row_fh_s" class="score-input" inputmode="numeric"></td>
                <td><input type="text" name="yamb_scoresheets-${formCount}-row_fh_total" class="score-input" inputmode="numeric" readonly></td>
              </tr>
              <tr><td><strong>C</strong></td>
                <td><input type="text" name="yamb_scoresheets-${formCount}-row_c_down" class="score-input" inputmode="numeric"></td>
                <td><input type="text" name="yamb_scoresheets-${formCount}-row_c_up" class="score-input" inputmode="numeric"></td>
                <td><input type="text" name="yamb_scoresheets-${formCount}-row_c_l" class="score-input" inputmode="numeric"></td>
                <td><input type="text" name="yamb_scoresheets-${formCount}-row_c_s" class="score-input" inputmode="numeric"></td>
                <td><input type="text" name="yamb_scoresheets-${formCount}-row_c_total" class="score-input" inputmode="numeric" readonly></td>
              </tr>
              <tr><td><strong>S</strong></td>
                <td><input type="text" name="yamb_scoresheets-${formCount}-row_s_down" class="score-input" inputmode="numeric"></td>
                <td><input type="text" name="yamb_scoresheets-${formCount}-row_s_up" class="score-input" inputmode="numeric"></td>
                <td><input type="text" name="yamb_scoresheets-${formCount}-row_s_l" class="score-input" inputmode="numeric"></td>
                <td><input type="text" name="yamb_scoresheets-${formCount}-row_s_s" class="score-input" inputmode="numeric"></td>
                <td><input type="text" name="yamb_scoresheets-${formCount}-row_s_total" class="score-input" inputmode="numeric" readonly></td>
              </tr>
              <tr><td><strong>P</strong></td>
                <td><input type="text" name="yamb_scoresheets-${formCount}-row_p_down" class="score-input" inputmode="numeric"></td>
                <td><input type="text" name="yamb_scoresheets-${formCount}-row_p_up" class="score-input" inputmode="numeric"></td>
                <td><input type="text" name="yamb_scoresheets-${formCount}-row_p_l" class="score-input" inputmode="numeric"></td>
                <td><input type="text" name="yamb_scoresheets-${formCount}-row_p_s" class="score-input" inputmode="numeric"></td>
                <td><input type="text" name="yamb_scoresheets-${formCount}-row_p_total" class="score-input" inputmode="numeric" readonly></td>
              </tr>
            </tbody>
          </table>
        </div>
        
        <div style="margin-top: 0.5rem;">
          <label><strong>Final Score:</strong> <input type="text" name="yamb_scoresheets-${formCount}-final_score" class="score-input" inputmode="numeric" readonly></label>
        </div>
        
        <input type="hidden" name="yamb_scoresheets-${formCount}-DELETE" id="id_yamb_scoresheets-${formCount}-DELETE">
      </div>
    `;
    return template;
  }
  
  // Remove scoresheet
  function removeScoresheet(e) {
    e.preventDefault();
    const wrapper = e.target.closest('.scoresheet-wrapper');
    
    // Check if scoresheet has any data
    const inputs = wrapper.querySelectorAll('input[type="text"]');
    let hasData = false;
    
    inputs.forEach(input => {
      if (input.value.trim() !== '' && !input.hasAttribute('readonly')) {
        hasData = true;
      }
    });
    
    // Get player name for the confirmation message
    const playerSelect = wrapper.querySelector('[name*="-player"]');
    const playerName = playerSelect && playerSelect.value ? 
      playerSelect.options[playerSelect.selectedIndex]?.text : 
      'this player';
    
    // If there's data, ask for confirmation
    if (hasData) {
      const message = `Remove scoresheet for ${playerName}? This has data and cannot be undone.`;
      if (!confirm(message)) {
        return; // Don't remove if user cancels
      }
    } else {
      // Even for empty sheets, ask for confirmation to prevent accidents
      const message = `Remove scoresheet for ${playerName}?`;
      if (!confirm(message)) {
        return;
      }
    }
    
    wrapper.remove();
  }
  
  // Calculate final score (sum of all row totals)
  function calculateFinalScore(wrapper) {
    const prefix = wrapper.querySelector('input[name*="row_1_total"]')?.name.split('-row_1_total')[0];
    if (!prefix) return;
    
    const finalScoreField = wrapper.querySelector(`input[name="${prefix}-final_score"]`);
    if (!finalScoreField) return;
    
    const totalFields = [
      'row_1_total', 'row_2_total', 'row_3_total', 'row_4_total',
      'row_5_total', 'row_6_total', 'row_h_total', 'row_l_total',
      'row_fh_total', 'row_c_total', 'row_s_total', 'row_p_total'
    ];
    
    let sum = 0;
    let allFilled = true;
    
    totalFields.forEach(fieldName => {
      const field = wrapper.querySelector(`input[name="${prefix}-${fieldName}"]`);
      if (field && field.value.trim() !== '') {
        sum += parseInt(field.value) || 0;
      } else {
        allFilled = false;
      }
    });
    
    if (allFilled) {
      finalScoreField.value = sum;
    } else {
      finalScoreField.value = '';
    }
  }
  
  // Row 1 calculation logic
  function calculateRow1Total(wrapper, showErrors = false) {
    const prefix = wrapper.querySelector('input[name*="row_1_down"]')?.name.split('-row_1_down')[0];
    if (!prefix) return;
    
    const downField = wrapper.querySelector(`input[name="${prefix}-row_1_down"]`);
    const upField = wrapper.querySelector(`input[name="${prefix}-row_1_up"]`);
    const lField = wrapper.querySelector(`input[name="${prefix}-row_1_l"]`);
    const sField = wrapper.querySelector(`input[name="${prefix}-row_1_s"]`);
    const totalField = wrapper.querySelector(`input[name="${prefix}-row_1_total"]`);
    const errorDiv = wrapper.querySelector('.row-1-error');
    
    if (!downField || !upField || !lField || !sField || !totalField) return;
    
    // Parse values - explicitly check for empty string to handle 0 properly
    const down = downField.value.trim() === '' ? null : parseInt(downField.value);
    const up = upField.value.trim() === '' ? null : parseInt(upField.value);
    const l = lField.value.trim() === '' ? null : parseInt(lField.value);
    const s = sField.value.trim() === '' ? null : parseInt(sField.value);
    
    // Validate that all non-null values are between 0-5
    const fields = [
      {name: '↓', value: down, field: downField},
      {name: '↑', value: up, field: upField},
      {name: 'L', value: l, field: lField},
      {name: 'S', value: s, field: sField}
    ];
    
    const errors = [];
    fields.forEach(f => {
      // Check if field has text but is not a valid number
      if (f.field.value.trim() !== '' && isNaN(f.value)) {
        errors.push(`${f.name} column: must be a number`);
        if (showErrors) {
          f.field.style.borderColor = '#c33';
          f.field.style.borderWidth = '2px';
        }
      } else if (f.value !== null && !isNaN(f.value) && (f.value < 0 || f.value > 5)) {
        errors.push(`${f.name} column: ${f.value} is invalid (must be 0-5)`);
        if (showErrors) {
          f.field.style.borderColor = '#c33';
          f.field.style.borderWidth = '2px';
        }
      } else {
        f.field.style.borderColor = '';
        f.field.style.borderWidth = '';
      }
    });
    
    // Show or hide error message (only if showErrors is true)
    if (errorDiv && showErrors) {
      if (errors.length > 0) {
        errorDiv.innerHTML = '<strong>Row 1 Error:</strong> ' + errors.join(', ');
        errorDiv.style.display = 'block';
        totalField.value = '';
        calculateFinalScore(wrapper);
        return;
      } else {
        errorDiv.style.display = 'none';
      }
    }
    
    // Calculate total if all four values are present (including 0) and valid
    if (down !== null && up !== null && l !== null && s !== null &&
        !isNaN(down) && !isNaN(up) && !isNaN(l) && !isNaN(s) && errors.length === 0) {
      const sum = down + up + l + s;
      const total = (sum - 12) * 10;
      totalField.value = total;
    } else {
      // Clear total if not all values are filled
      totalField.value = '';
    }
    calculateFinalScore(wrapper);
  }
  
  // Attach input listeners to all Row 1 fields
  function attachRow1Listeners(wrapper) {
    const prefix = wrapper.querySelector('input[name*="row_1_down"]')?.name.split('-row_1_down')[0];
    if (!prefix) return;
    
    ['row_1_down', 'row_1_up', 'row_1_l', 'row_1_s'].forEach(fieldName => {
      const field = wrapper.querySelector(`input[name="${prefix}-${fieldName}"]`);
      if (field) {
        field.addEventListener('input', () => calculateRow1Total(wrapper, false));
        field.addEventListener('blur', () => calculateRow1Total(wrapper, true));
      }
    });
  }
  
  // Row 2 calculation logic (same as Row 1 but multiply by 20)
  function calculateRow2Total(wrapper, showErrors = false) {
    const prefix = wrapper.querySelector('input[name*="row_2_down"]')?.name.split('-row_2_down')[0];
    if (!prefix) return;
    
    const downField = wrapper.querySelector(`input[name="${prefix}-row_2_down"]`);
    const upField = wrapper.querySelector(`input[name="${prefix}-row_2_up"]`);
    const lField = wrapper.querySelector(`input[name="${prefix}-row_2_l"]`);
    const sField = wrapper.querySelector(`input[name="${prefix}-row_2_s"]`);
    const totalField = wrapper.querySelector(`input[name="${prefix}-row_2_total"]`);
    const errorDiv = wrapper.querySelector('.row-2-error');
    
    if (!downField || !upField || !lField || !sField || !totalField) return;
    
    // Parse values - explicitly check for empty string to handle 0 properly
    const down = downField.value.trim() === '' ? null : parseInt(downField.value);
    const up = upField.value.trim() === '' ? null : parseInt(upField.value);
    const l = lField.value.trim() === '' ? null : parseInt(lField.value);
    const s = sField.value.trim() === '' ? null : parseInt(sField.value);
    
    // Validate that all non-null values are between 0-5
    const fields = [
      {name: '↓', value: down, field: downField},
      {name: '↑', value: up, field: upField},
      {name: 'L', value: l, field: lField},
      {name: 'S', value: s, field: sField}
    ];
    
    const errors = [];
    fields.forEach(f => {
      // Check if field has text but is not a valid number
      if (f.field.value.trim() !== '' && isNaN(f.value)) {
        errors.push(`${f.name} column: must be a number`);
        if (showErrors) {
          f.field.style.borderColor = '#c33';
          f.field.style.borderWidth = '2px';
        }
      } else if (f.value !== null && !isNaN(f.value) && (f.value < 0 || f.value > 5)) {
        errors.push(`${f.name} column: ${f.value} is invalid (must be 0-5)`);
        if (showErrors) {
          f.field.style.borderColor = '#c33';
          f.field.style.borderWidth = '2px';
        }
      } else {
        f.field.style.borderColor = '';
        f.field.style.borderWidth = '';
      }
    });
    
    // Show or hide error message
    if (errorDiv && showErrors) {
      if (errors.length > 0) {
        errorDiv.innerHTML = '<strong>Row 2 Error:</strong> ' + errors.join(', ');
        errorDiv.style.display = 'block';
        totalField.value = '';
        calculateFinalScore(wrapper);
        return;
      } else {
        errorDiv.style.display = 'none';
      }
    }
    
    // Calculate total if all four values are present (including 0) and valid
    if (down !== null && up !== null && l !== null && s !== null &&
        !isNaN(down) && !isNaN(up) && !isNaN(l) && !isNaN(s) && errors.length === 0) {
      const sum = down + up + l + s;
      const total = (sum - 12) * 20;  // Row 2 uses 20 instead of 10
      totalField.value = total;
    } else {
      // Clear total if not all values are filled
      totalField.value = '';
    }
    calculateFinalScore(wrapper);
  }
  
  // Attach input listeners to all Row 2 fields
  function attachRow2Listeners(wrapper) {
    const prefix = wrapper.querySelector('input[name*="row_2_down"]')?.name.split('-row_2_down')[0];
    if (!prefix) return;
    
    ['row_2_down', 'row_2_up', 'row_2_l', 'row_2_s'].forEach(fieldName => {
      const field = wrapper.querySelector(`input[name="${prefix}-${fieldName}"]`);
      if (field) {
        field.addEventListener('input', () => calculateRow2Total(wrapper, false));
        field.addEventListener('blur', () => calculateRow2Total(wrapper, true));
      }
    });
  }
  
  // Helper function to create calculation function for rows 3-6
  function createRowCalculator(rowNum, multiplier) {
    return function(wrapper, showErrors = false) {
      const prefix = wrapper.querySelector(`input[name*="row_${rowNum}_down"]`)?.name.split(`-row_${rowNum}_down`)[0];
      if (!prefix) return;
      
      const downField = wrapper.querySelector(`input[name="${prefix}-row_${rowNum}_down"]`);
      const upField = wrapper.querySelector(`input[name="${prefix}-row_${rowNum}_up"]`);
      const lField = wrapper.querySelector(`input[name="${prefix}-row_${rowNum}_l"]`);
      const sField = wrapper.querySelector(`input[name="${prefix}-row_${rowNum}_s"]`);
      const totalField = wrapper.querySelector(`input[name="${prefix}-row_${rowNum}_total"]`);
      const errorDiv = wrapper.querySelector(`.row-${rowNum}-error`);
      
      if (!downField || !upField || !lField || !sField || !totalField) return;
      
      const down = downField.value.trim() === '' ? null : parseInt(downField.value);
      const up = upField.value.trim() === '' ? null : parseInt(upField.value);
      const l = lField.value.trim() === '' ? null : parseInt(lField.value);
      const s = sField.value.trim() === '' ? null : parseInt(sField.value);
      
      const fields = [
        {name: '↓', value: down, field: downField},
        {name: '↑', value: up, field: upField},
        {name: 'L', value: l, field: lField},
        {name: 'S', value: s, field: sField}
      ];
      
      const errors = [];
      fields.forEach(f => {
        // Check if field has text but is not a valid number
        if (f.field.value.trim() !== '' && isNaN(f.value)) {
          errors.push(`${f.name} column: must be a number`);
          if (showErrors) {
            f.field.style.borderColor = '#c33';
            f.field.style.borderWidth = '2px';
          }
        } else if (f.value !== null && !isNaN(f.value) && (f.value < 0 || f.value > 5)) {
          errors.push(`${f.name} column: ${f.value} is invalid (must be 0-5)`);
          if (showErrors) {
            f.field.style.borderColor = '#c33';
            f.field.style.borderWidth = '2px';
          }
        } else {
          f.field.style.borderColor = '';
          f.field.style.borderWidth = '';
        }
      });
      
      if (errors.length > 0) {
        if (errorDiv && showErrors) {
          errorDiv.innerHTML = `<strong>Row ${rowNum} Error:</strong> ` + errors.join(', ');
          errorDiv.style.display = 'block';
        }
        totalField.value = '';
        calculateFinalScore(wrapper);
        return;
      } else {
        if (errorDiv) {
          errorDiv.style.display = 'none';
        }
      }
      
      if (down !== null && up !== null && l !== null && s !== null &&
          !isNaN(down) && !isNaN(up) && !isNaN(l) && !isNaN(s)) {
        const sum = down + up + l + s;
        const total = (sum - 12) * multiplier;
        totalField.value = total;
      } else {
        totalField.value = '';
      }
      calculateFinalScore(wrapper);
    };
  }
  
  // Create calculation functions for rows 3-6
  const calculateRow3Total = createRowCalculator(3, 30);
  const calculateRow4Total = createRowCalculator(4, 40);
  const calculateRow5Total = createRowCalculator(5, 50);
  const calculateRow6Total = createRowCalculator(6, 60);
  
  // Helper function to create listener attachment for rows 3-6
  function createRowListenerAttacher(rowNum, calculator) {
    return function(wrapper) {
      const prefix = wrapper.querySelector(`input[name*="row_${rowNum}_down"]`)?.name.split(`-row_${rowNum}_down`)[0];
      if (!prefix) return;
      
      [`row_${rowNum}_down`, `row_${rowNum}_up`, `row_${rowNum}_l`, `row_${rowNum}_s`].forEach(fieldName => {
        const field = wrapper.querySelector(`input[name="${prefix}-${fieldName}"]`);
        if (field) {
          field.addEventListener('input', () => calculator(wrapper, false));
          field.addEventListener('blur', () => calculator(wrapper, true));
        }
      });
    };
  }
  
  // Create listener attachers for rows 3-6
  const attachRow3Listeners = createRowListenerAttacher(3, calculateRow3Total);
  const attachRow4Listeners = createRowListenerAttacher(4, calculateRow4Total);
  const attachRow5Listeners = createRowListenerAttacher(5, calculateRow5Total);
  const attachRow6Listeners = createRowListenerAttacher(6, calculateRow6Total);
  
  // Row H and L calculation (simple sum, range 0-30)
  function calculateRowHTotal(wrapper, showErrors = false) {
    const prefix = wrapper.querySelector('input[name*="row_h_down"]')?.name.split('-row_h_down')[0];
    if (!prefix) return;
    
    // Get H row fields
    const downField = wrapper.querySelector(`input[name="${prefix}-row_h_down"]`);
    const upField = wrapper.querySelector(`input[name="${prefix}-row_h_up"]`);
    const lField = wrapper.querySelector(`input[name="${prefix}-row_h_l"]`);
    const sField = wrapper.querySelector(`input[name="${prefix}-row_h_s"]`);
    const totalField = wrapper.querySelector(`input[name="${prefix}-row_h_total"]`);
    
    // Get L row fields
    const lDownField = wrapper.querySelector(`input[name="${prefix}-row_l_down"]`);
    const lUpField = wrapper.querySelector(`input[name="${prefix}-row_l_up"]`);
    const lLField = wrapper.querySelector(`input[name="${prefix}-row_l_l"]`);
    const lSField = wrapper.querySelector(`input[name="${prefix}-row_l_s"]`);
    
    const errorDiv = wrapper.querySelector('.row-h-error');
    
    if (!downField || !upField || !lField || !sField || !totalField ||
        !lDownField || !lUpField || !lLField || !lSField) return;
    
    // Parse H values
    const down = downField.value.trim() === '' ? null : parseInt(downField.value);
    const up = upField.value.trim() === '' ? null : parseInt(upField.value);
    const l = lField.value.trim() === '' ? null : parseInt(lField.value);
    const s = sField.value.trim() === '' ? null : parseInt(sField.value);
    
    // Parse L values
    const lDown = lDownField.value.trim() === '' ? null : parseInt(lDownField.value);
    const lUp = lUpField.value.trim() === '' ? null : parseInt(lUpField.value);
    const lL = lLField.value.trim() === '' ? null : parseInt(lLField.value);
    const lS = lSField.value.trim() === '' ? null : parseInt(lSField.value);
    
    const fields = [
      {name: 'H ↓', value: down, field: downField},
      {name: 'H ↑', value: up, field: upField},
      {name: 'H L', value: l, field: lField},
      {name: 'H S', value: s, field: sField}
    ];
    
    const errors = [];
    
    // Validate range for H row
    fields.forEach(f => {
      // Check if field has text but is not a valid number
      if (f.field.value.trim() !== '' && isNaN(f.value)) {
        errors.push(`${f.name}: must be a number`);
        if (showErrors) {
          f.field.style.borderColor = '#c33';
          f.field.style.borderWidth = '2px';
        }
      } else if (f.value !== null && !isNaN(f.value) && (f.value < 0 || f.value > 30)) {
        errors.push(`${f.name}: ${f.value} is invalid (must be 0-30)`);
        if (showErrors) {
          f.field.style.borderColor = '#c33';
          f.field.style.borderWidth = '2px';
        }
      } else {
        f.field.style.borderColor = '';
        f.field.style.borderWidth = '';
      }
    });
    
    // Validate H > L for each column (only if both values present)
    // Exception: both can be 0
    if (down !== null && lDown !== null && down <= lDown && !(down === 0 && lDown === 0)) {
      errors.push(`H ↓ (${down}) must be greater than L ↓ (${lDown})`);
      if (showErrors) {
        downField.style.borderColor = '#c33';
        downField.style.borderWidth = '2px';
      }
    }
    if (up !== null && lUp !== null && up <= lUp && !(up === 0 && lUp === 0)) {
      errors.push(`H ↑ (${up}) must be greater than L ↑ (${lUp})`);
      if (showErrors) {
        upField.style.borderColor = '#c33';
        upField.style.borderWidth = '2px';
      }
    }
    if (l !== null && lL !== null && l <= lL && !(l === 0 && lL === 0)) {
      errors.push(`H L (${l}) must be greater than L L (${lL})`);
      if (showErrors) {
        lField.style.borderColor = '#c33';
        lField.style.borderWidth = '2px';
      }
    }
    if (s !== null && lS !== null && s <= lS && !(s === 0 && lS === 0)) {
      errors.push(`H S (${s}) must be greater than L S (${lS})`);
      if (showErrors) {
        sField.style.borderColor = '#c33';
        sField.style.borderWidth = '2px';
      }
    }
    
    if (errors.length > 0) {
      if (errorDiv && showErrors) {
        errorDiv.innerHTML = '<strong>Row H/L Error:</strong> ' + errors.join(', ');
        errorDiv.style.display = 'block';
      }
      totalField.value = '';
      calculateFinalScore(wrapper);
      return;
    } else {
      if (errorDiv) {
        errorDiv.style.display = 'none';
      }
    }
    
    // Only calculate when ALL 8 cells are filled
    if (down !== null && up !== null && l !== null && s !== null &&
        lDown !== null && lUp !== null && lL !== null && lS !== null &&
        !isNaN(down) && !isNaN(up) && !isNaN(l) && !isNaN(s) &&
        !isNaN(lDown) && !isNaN(lUp) && !isNaN(lL) && !isNaN(lS)) {
      
      // Calculate bonuses: 30 for each column where H + L >= 50
      // Add green box around bonus pairs
      let bonuses = 0;
      if (down + lDown >= 50) {
        bonuses += 30;
        downField.style.borderColor = '#22dd55';
        downField.style.borderWidth = '2px';
        lDownField.style.borderColor = '#22dd55';
        lDownField.style.borderWidth = '2px';
      } else if (errors.length === 0) {
        // Only clear green if no errors
        downField.style.borderColor = '';
        downField.style.borderWidth = '';
        lDownField.style.borderColor = '';
        lDownField.style.borderWidth = '';
      }
      
      if (up + lUp >= 50) {
        bonuses += 30;
        upField.style.borderColor = '#22dd55';
        upField.style.borderWidth = '2px';
        lUpField.style.borderColor = '#22dd55';
        lUpField.style.borderWidth = '2px';
      } else if (errors.length === 0) {
        upField.style.borderColor = '';
        upField.style.borderWidth = '';
        lUpField.style.borderColor = '';
        lUpField.style.borderWidth = '';
      }
      
      if (l + lL >= 50) {
        bonuses += 30;
        lField.style.borderColor = '#22dd55';
        lField.style.borderWidth = '2px';
        lLField.style.borderColor = '#22dd55';
        lLField.style.borderWidth = '2px';
      } else if (errors.length === 0) {
        lField.style.borderColor = '';
        lField.style.borderWidth = '';
        lLField.style.borderColor = '';
        lLField.style.borderWidth = '';
      }
      
      if (s + lS >= 50) {
        bonuses += 30;
        sField.style.borderColor = '#22dd55';
        sField.style.borderWidth = '2px';
        lSField.style.borderColor = '#22dd55';
        lSField.style.borderWidth = '2px';
      } else if (errors.length === 0) {
        sField.style.borderColor = '';
        sField.style.borderWidth = '';
        lSField.style.borderColor = '';
        lSField.style.borderWidth = '';
      }
      
      const total = down + up + l + s + bonuses;
      totalField.value = total;
    } else {
      totalField.value = '';
    }
    calculateFinalScore(wrapper);
  }
  
  function calculateRowLTotal(wrapper, showErrors = false) {
    const prefix = wrapper.querySelector('input[name*="row_l_down"]')?.name.split('-row_l_down')[0];
    if (!prefix) return;
    
    // Get L row fields
    const downField = wrapper.querySelector(`input[name="${prefix}-row_l_down"]`);
    const upField = wrapper.querySelector(`input[name="${prefix}-row_l_up"]`);
    const lField = wrapper.querySelector(`input[name="${prefix}-row_l_l"]`);
    const sField = wrapper.querySelector(`input[name="${prefix}-row_l_s"]`);
    const totalField = wrapper.querySelector(`input[name="${prefix}-row_l_total"]`);
    
    // Get H row fields
    const hDownField = wrapper.querySelector(`input[name="${prefix}-row_h_down"]`);
    const hUpField = wrapper.querySelector(`input[name="${prefix}-row_h_up"]`);
    const hLField = wrapper.querySelector(`input[name="${prefix}-row_h_l"]`);
    const hSField = wrapper.querySelector(`input[name="${prefix}-row_h_s"]`);
    
    const errorDiv = wrapper.querySelector('.row-l-error');
    
    if (!downField || !upField || !lField || !sField || !totalField ||
        !hDownField || !hUpField || !hLField || !hSField) return;
    
    // Parse L values
    const down = downField.value.trim() === '' ? null : parseInt(downField.value);
    const up = upField.value.trim() === '' ? null : parseInt(upField.value);
    const l = lField.value.trim() === '' ? null : parseInt(lField.value);
    const s = sField.value.trim() === '' ? null : parseInt(sField.value);
    
    // Parse H values
    const hDown = hDownField.value.trim() === '' ? null : parseInt(hDownField.value);
    const hUp = hUpField.value.trim() === '' ? null : parseInt(hUpField.value);
    const hL = hLField.value.trim() === '' ? null : parseInt(hLField.value);
    const hS = hSField.value.trim() === '' ? null : parseInt(hSField.value);
    
    const fields = [
      {name: 'L ↓', value: down, field: downField},
      {name: 'L ↑', value: up, field: upField},
      {name: 'L L', value: l, field: lField},
      {name: 'L S', value: s, field: sField}
    ];
    
    const errors = [];
    
    // Validate range for L row
    fields.forEach(f => {
      // Check if field has text but is not a valid number
      if (f.field.value.trim() !== '' && isNaN(f.value)) {
        errors.push(`${f.name}: must be a number`);
        if (showErrors) {
          f.field.style.borderColor = '#c33';
          f.field.style.borderWidth = '2px';
        }
      } else if (f.value !== null && !isNaN(f.value) && (f.value < 0 || f.value > 30)) {
        errors.push(`${f.name}: ${f.value} is invalid (must be 0-30)`);
        if (showErrors) {
          f.field.style.borderColor = '#c33';
          f.field.style.borderWidth = '2px';
        }
      } else {
        f.field.style.borderColor = '';
        f.field.style.borderWidth = '';
      }
    });
    
    // Validate L < H for each column (only if both values present)
    // Exception: both can be 0
    if (down !== null && hDown !== null && down >= hDown && !(down === 0 && hDown === 0)) {
      errors.push(`L ↓ (${down}) must be less than H ↓ (${hDown})`);
      if (showErrors) {
        downField.style.borderColor = '#c33';
        downField.style.borderWidth = '2px';
      }
    }
    if (up !== null && hUp !== null && up >= hUp && !(up === 0 && hUp === 0)) {
      errors.push(`L ↑ (${up}) must be less than H ↑ (${hUp})`);
      if (showErrors) {
        upField.style.borderColor = '#c33';
        upField.style.borderWidth = '2px';
      }
    }
    if (l !== null && hL !== null && l >= hL && !(l === 0 && hL === 0)) {
      errors.push(`L L (${l}) must be less than H L (${hL})`);
      if (showErrors) {
        lField.style.borderColor = '#c33';
        lField.style.borderWidth = '2px';
      }
    }
    if (s !== null && hS !== null && s >= hS && !(s === 0 && hS === 0)) {
      errors.push(`L S (${s}) must be less than H S (${hS})`);
      if (showErrors) {
        sField.style.borderColor = '#c33';
        sField.style.borderWidth = '2px';
      }
    }
    
    if (errors.length > 0) {
      if (errorDiv && showErrors) {
        errorDiv.innerHTML = '<strong>Row H/L Error:</strong> ' + errors.join(', ');
        errorDiv.style.display = 'block';
      }
      totalField.value = '';
      calculateFinalScore(wrapper);
      return;
    } else {
      if (errorDiv) {
        errorDiv.style.display = 'none';
      }
    }
    
    // Only calculate when ALL 8 cells are filled
    if (down !== null && up !== null && l !== null && s !== null &&
        hDown !== null && hUp !== null && hL !== null && hS !== null &&
        !isNaN(down) && !isNaN(up) && !isNaN(l) && !isNaN(s) &&
        !isNaN(hDown) && !isNaN(hUp) && !isNaN(hL) && !isNaN(hS)) {
      
      const total = down + up + l + s;  // Simple sum (no bonuses on L row)
      totalField.value = total;
    } else {
      totalField.value = '';
    }
    calculateFinalScore(wrapper);
  }
  
  function attachRowHListeners(wrapper) {
    const prefix = wrapper.querySelector('input[name*="row_h_down"]')?.name.split('-row_h_down')[0];
    if (!prefix) return;
    
    // Attach listeners to H fields - recalculate both H and L when H changes
    ['row_h_down', 'row_h_up', 'row_h_l', 'row_h_s'].forEach(fieldName => {
      const field = wrapper.querySelector(`input[name="${prefix}-${fieldName}"]`);
      if (field) {
        field.addEventListener('input', () => {
          calculateRowHTotal(wrapper, false);
          calculateRowLTotal(wrapper, false);
        });
        field.addEventListener('blur', () => {
          calculateRowHTotal(wrapper, true);
          calculateRowLTotal(wrapper, true);
        });
      }
    });
  }
  
  function attachRowLListeners(wrapper) {
    const prefix = wrapper.querySelector('input[name*="row_l_down"]')?.name.split('-row_l_down')[0];
    if (!prefix) return;
    
    // Attach listeners to L fields - recalculate both H and L when L changes
    ['row_l_down', 'row_l_up', 'row_l_l', 'row_l_s'].forEach(fieldName => {
      const field = wrapper.querySelector(`input[name="${prefix}-${fieldName}"]`);
      if (field) {
        field.addEventListener('input', () => {
          calculateRowHTotal(wrapper, false);
          calculateRowLTotal(wrapper, false);
        });
        field.addEventListener('blur', () => {
          calculateRowHTotal(wrapper, true);
          calculateRowLTotal(wrapper, true);
        });
      }
    });
  }
  
  // FH row calculation: sum of 4 cells, valid values are 40 or 0
  function calculateRowFHTotal(wrapper, showErrors = false) {
    const prefix = wrapper.querySelector('input[name*="row_fh_down"]')?.name.split('-row_fh_down')[0];
    if (!prefix) return;
    
    const downField = wrapper.querySelector(`input[name="${prefix}-row_fh_down"]`);
    const upField = wrapper.querySelector(`input[name="${prefix}-row_fh_up"]`);
    const lField = wrapper.querySelector(`input[name="${prefix}-row_fh_l"]`);
    const sField = wrapper.querySelector(`input[name="${prefix}-row_fh_s"]`);
    const totalField = wrapper.querySelector(`input[name="${prefix}-row_fh_total"]`);
    const errorDiv = wrapper.querySelector('.row-fh-error');
    
    if (!downField || !upField || !lField || !sField || !totalField) return;
    
    const down = downField.value.trim() === '' ? null : parseInt(downField.value);
    const up = upField.value.trim() === '' ? null : parseInt(upField.value);
    const l = lField.value.trim() === '' ? null : parseInt(lField.value);
    const s = sField.value.trim() === '' ? null : parseInt(sField.value);
    
    const fields = [
      {name: '↓', value: down, field: downField},
      {name: '↑', value: up, field: upField},
      {name: 'L', value: l, field: lField},
      {name: 'S', value: s, field: sField}
    ];
    
    const errors = [];
    fields.forEach(f => {
      // Check if field has text but is not a valid number
      if (f.field.value.trim() !== '' && isNaN(f.value)) {
        errors.push(`${f.name}: must be a number`);
        if (showErrors) {
          f.field.style.borderColor = '#c33';
          f.field.style.borderWidth = '2px';
        }
      } else if (f.value !== null && !isNaN(f.value) && f.value !== 0 && f.value !== 40) {
        errors.push(`${f.name}: ${f.value} is invalid (must be 0 or 40)`);
        if (showErrors) {
          f.field.style.borderColor = '#c33';
          f.field.style.borderWidth = '2px';
        }
      } else {
        f.field.style.borderColor = '';
        f.field.style.borderWidth = '';
      }
    });
    
    if (errors.length > 0) {
      if (errorDiv && showErrors) {
        errorDiv.innerHTML = '<strong>Row FH Error:</strong> ' + errors.join(', ');
        errorDiv.style.display = 'block';
      }
      totalField.value = '';
      calculateFinalScore(wrapper);
      return;
    } else {
      if (errorDiv) {
        errorDiv.style.display = 'none';
      }
    }
    
    if (down !== null && up !== null && l !== null && s !== null &&
        !isNaN(down) && !isNaN(up) && !isNaN(l) && !isNaN(s)) {
      const total = down + up + l + s;
      totalField.value = total;
    } else {
      totalField.value = '';
    }
    calculateFinalScore(wrapper);
  }
  
  // C row calculation: sum of 4 cells, valid values are 60 or 0
  function calculateRowCTotal(wrapper, showErrors = false) {
    const prefix = wrapper.querySelector('input[name*="row_c_down"]')?.name.split('-row_c_down')[0];
    if (!prefix) return;
    
    const downField = wrapper.querySelector(`input[name="${prefix}-row_c_down"]`);
    const upField = wrapper.querySelector(`input[name="${prefix}-row_c_up"]`);
    const lField = wrapper.querySelector(`input[name="${prefix}-row_c_l"]`);
    const sField = wrapper.querySelector(`input[name="${prefix}-row_c_s"]`);
    const totalField = wrapper.querySelector(`input[name="${prefix}-row_c_total"]`);
    const errorDiv = wrapper.querySelector('.row-c-error');
    
    if (!downField || !upField || !lField || !sField || !totalField) return;
    
    const down = downField.value.trim() === '' ? null : parseInt(downField.value);
    const up = upField.value.trim() === '' ? null : parseInt(upField.value);
    const l = lField.value.trim() === '' ? null : parseInt(lField.value);
    const s = sField.value.trim() === '' ? null : parseInt(sField.value);
    
    const fields = [
      {name: '↓', value: down, field: downField},
      {name: '↑', value: up, field: upField},
      {name: 'L', value: l, field: lField},
      {name: 'S', value: s, field: sField}
    ];
    
    const errors = [];
    fields.forEach(f => {
      // Check if field has text but is not a valid number
      if (f.field.value.trim() !== '' && isNaN(f.value)) {
        errors.push(`${f.name}: must be a number`);
        if (showErrors) {
          f.field.style.borderColor = '#c33';
          f.field.style.borderWidth = '2px';
        }
      } else if (f.value !== null && !isNaN(f.value) && f.value !== 0 && f.value !== 60) {
        errors.push(`${f.name}: ${f.value} is invalid (must be 0 or 60)`);
        if (showErrors) {
          f.field.style.borderColor = '#c33';
          f.field.style.borderWidth = '2px';
        }
      } else {
        f.field.style.borderColor = '';
        f.field.style.borderWidth = '';
      }
    });
    
    if (errors.length > 0) {
      if (errorDiv && showErrors) {
        errorDiv.innerHTML = '<strong>Row C Error:</strong> ' + errors.join(', ');
        errorDiv.style.display = 'block';
      }
      totalField.value = '';
      calculateFinalScore(wrapper);
      return;
    } else {
      if (errorDiv) {
        errorDiv.style.display = 'none';
      }
    }
    
    if (down !== null && up !== null && l !== null && s !== null &&
        !isNaN(down) && !isNaN(up) && !isNaN(l) && !isNaN(s)) {
      const total = down + up + l + s;
      totalField.value = total;
    } else {
      totalField.value = '';
    }
    calculateFinalScore(wrapper);
  }
  
  // S row calculation: sum of 4 cells, valid values are 80 or 0
  function calculateRowSTotal(wrapper, showErrors = false) {
    const prefix = wrapper.querySelector('input[name*="row_s_down"]')?.name.split('-row_s_down')[0];
    if (!prefix) return;
    
    const downField = wrapper.querySelector(`input[name="${prefix}-row_s_down"]`);
    const upField = wrapper.querySelector(`input[name="${prefix}-row_s_up"]`);
    const lField = wrapper.querySelector(`input[name="${prefix}-row_s_l"]`);
    const sField = wrapper.querySelector(`input[name="${prefix}-row_s_s"]`);
    const totalField = wrapper.querySelector(`input[name="${prefix}-row_s_total"]`);
    const errorDiv = wrapper.querySelector('.row-s-error');
    
    if (!downField || !upField || !lField || !sField || !totalField) return;
    
    const down = downField.value.trim() === '' ? null : parseInt(downField.value);
    const up = upField.value.trim() === '' ? null : parseInt(upField.value);
    const l = lField.value.trim() === '' ? null : parseInt(lField.value);
    const s = sField.value.trim() === '' ? null : parseInt(sField.value);
    
    const fields = [
      {name: '↓', value: down, field: downField},
      {name: '↑', value: up, field: upField},
      {name: 'L', value: l, field: lField},
      {name: 'S', value: s, field: sField}
    ];
    
    const errors = [];
    fields.forEach(f => {
      // Check if field has text but is not a valid number
      if (f.field.value.trim() !== '' && isNaN(f.value)) {
        errors.push(`${f.name}: must be a number`);
        if (showErrors) {
          f.field.style.borderColor = '#c33';
          f.field.style.borderWidth = '2px';
        }
      } else if (f.value !== null && !isNaN(f.value) && f.value !== 0 && f.value !== 80) {
        errors.push(`${f.name}: ${f.value} is invalid (must be 0 or 80)`);
        if (showErrors) {
          f.field.style.borderColor = '#c33';
          f.field.style.borderWidth = '2px';
        }
      } else {
        f.field.style.borderColor = '';
        f.field.style.borderWidth = '';
      }
    });
    
    if (errors.length > 0) {
      if (errorDiv && showErrors) {
        errorDiv.innerHTML = '<strong>Row S Error:</strong> ' + errors.join(', ');
        errorDiv.style.display = 'block';
      }
      totalField.value = '';
      calculateFinalScore(wrapper);
      return;
    } else {
      if (errorDiv) {
        errorDiv.style.display = 'none';
      }
    }
    
    if (down !== null && up !== null && l !== null && s !== null &&
        !isNaN(down) && !isNaN(up) && !isNaN(l) && !isNaN(s)) {
      const total = down + up + l + s;
      totalField.value = total;
    } else {
      totalField.value = '';
    }
    calculateFinalScore(wrapper);
  }
  
  // P row calculation: sum of 4 cells, valid values are 100 or 0
  function calculateRowPTotal(wrapper, showErrors = false) {
    const prefix = wrapper.querySelector('input[name*="row_p_down"]')?.name.split('-row_p_down')[0];
    if (!prefix) return;
    
    const downField = wrapper.querySelector(`input[name="${prefix}-row_p_down"]`);
    const upField = wrapper.querySelector(`input[name="${prefix}-row_p_up"]`);
    const lField = wrapper.querySelector(`input[name="${prefix}-row_p_l"]`);
    const sField = wrapper.querySelector(`input[name="${prefix}-row_p_s"]`);
    const totalField = wrapper.querySelector(`input[name="${prefix}-row_p_total"]`);
    const errorDiv = wrapper.querySelector('.row-p-error');
    
    if (!downField || !upField || !lField || !sField || !totalField) return;
    
    const down = downField.value.trim() === '' ? null : parseInt(downField.value);
    const up = upField.value.trim() === '' ? null : parseInt(upField.value);
    const l = lField.value.trim() === '' ? null : parseInt(lField.value);
    const s = sField.value.trim() === '' ? null : parseInt(sField.value);
    
    const fields = [
      {name: '↓', value: down, field: downField},
      {name: '↑', value: up, field: upField},
      {name: 'L', value: l, field: lField},
      {name: 'S', value: s, field: sField}
    ];
    
    const errors = [];
    fields.forEach(f => {
      // Check if field has text but is not a valid number
      if (f.field.value.trim() !== '' && isNaN(f.value)) {
        errors.push(`${f.name}: must be a number`);
        if (showErrors) {
          f.field.style.borderColor = '#c33';
          f.field.style.borderWidth = '2px';
        }
      } else if (f.value !== null && !isNaN(f.value) && f.value !== 0 && f.value !== 100) {
        errors.push(`${f.name}: ${f.value} is invalid (must be 0 or 100)`);
        if (showErrors) {
          f.field.style.borderColor = '#c33';
          f.field.style.borderWidth = '2px';
        }
      } else {
        f.field.style.borderColor = '';
        f.field.style.borderWidth = '';
      }
    });
    
    if (errors.length > 0) {
      if (errorDiv && showErrors) {
        errorDiv.innerHTML = '<strong>Row P Error:</strong> ' + errors.join(', ');
        errorDiv.style.display = 'block';
      }
      totalField.value = '';
      calculateFinalScore(wrapper);
      return;
    } else {
      if (errorDiv) {
        errorDiv.style.display = 'none';
      }
    }
    
    if (down !== null && up !== null && l !== null && s !== null &&
        !isNaN(down) && !isNaN(up) && !isNaN(l) && !isNaN(s)) {
      const total = down + up + l + s;
      totalField.value = total;
    } else {
      totalField.value = '';
    }
    calculateFinalScore(wrapper);
  }
  
  function attachRowFHListeners(wrapper) {
    const prefix = wrapper.querySelector('input[name*="row_fh_down"]')?.name.split('-row_fh_down')[0];
    if (!prefix) return;
    
    ['row_fh_down', 'row_fh_up', 'row_fh_l', 'row_fh_s'].forEach(fieldName => {
      const field = wrapper.querySelector(`input[name="${prefix}-${fieldName}"]`);
      if (field) {
        field.addEventListener('input', () => calculateRowFHTotal(wrapper, false));
        field.addEventListener('blur', () => calculateRowFHTotal(wrapper, true));
      }
    });
  }
  
  function attachRowCListeners(wrapper) {
    const prefix = wrapper.querySelector('input[name*="row_c_down"]')?.name.split('-row_c_down')[0];
    if (!prefix) return;
    
    ['row_c_down', 'row_c_up', 'row_c_l', 'row_c_s'].forEach(fieldName => {
      const field = wrapper.querySelector(`input[name="${prefix}-${fieldName}"]`);
      if (field) {
        field.addEventListener('input', () => calculateRowCTotal(wrapper, false));
        field.addEventListener('blur', () => calculateRowCTotal(wrapper, true));
      }
    });
  }
  
  function attachRowSListeners(wrapper) {
    const prefix = wrapper.querySelector('input[name*="row_s_down"]')?.name.split('-row_s_down')[0];
    if (!prefix) return;
    
    ['row_s_down', 'row_s_up', 'row_s_l', 'row_s_s'].forEach(fieldName => {
      const field = wrapper.querySelector(`input[name="${prefix}-${fieldName}"]`);
      if (field) {
        field.addEventListener('input', () => calculateRowSTotal(wrapper, false));
        field.addEventListener('blur', () => calculateRowSTotal(wrapper, true));
      }
    });
  }
  
  function attachRowPListeners(wrapper) {
    const prefix = wrapper.querySelector('input[name*="row_p_down"]')?.name.split('-row_p_down')[0];
    if (!prefix) return;
    
    ['row_p_down', 'row_p_up', 'row_p_l', 'row_p_s'].forEach(fieldName => {
      const field = wrapper.querySelector(`input[name="${prefix}-${fieldName}"]`);
      if (field) {
        field.addEventListener('input', () => calculateRowPTotal(wrapper, false));
        field.addEventListener('blur', () => calculateRowPTotal(wrapper, true));
      }
    });
  }
  
  // Add new scoresheet
  addBtn.addEventListener('click', function(e) {
    e.preventDefault();
    const formCount = parseInt(totalFormsInput.value);
    const newForm = createNewScoresheet(formCount);
    container.insertAdjacentHTML('beforeend', newForm);
    totalFormsInput.value = formCount + 1;
    
    // Get the newly added wrapper
    const newWrapper = container.lastElementChild;
    
    // Attach remove handler to the new X button
    const removeBtn = newWrapper.querySelector('.remove-scoresheet');
    if (removeBtn) {
      removeBtn.addEventListener('click', removeScoresheet);
    }
    
    // Attach Row 1 and Row 2 calculation listeners
    attachRow1Listeners(newWrapper);
    attachRow2Listeners(newWrapper);
    attachRow3Listeners(newWrapper);
    attachRow4Listeners(newWrapper);
    attachRow5Listeners(newWrapper);
    attachRow6Listeners(newWrapper);
    attachRowHListeners(newWrapper);
    attachRowLListeners(newWrapper);
    attachRowFHListeners(newWrapper);
    attachRowCListeners(newWrapper);
    attachRowSListeners(newWrapper);
    attachRowPListeners(newWrapper);
  });
  
  // Attach remove handlers to existing X buttons
  document.querySelectorAll('.remove-scoresheet').forEach(btn => {
    btn.addEventListener('click', removeScoresheet);
  });
  
  // Attach listeners to existing scoresheets
  document.querySelectorAll('.scoresheet-wrapper').forEach(wrapper => {
    attachRow1Listeners(wrapper);
    attachRow2Listeners(wrapper);
    attachRow3Listeners(wrapper);
    attachRow4Listeners(wrapper);
    attachRow5Listeners(wrapper);
    attachRow6Listeners(wrapper);
    attachRowHListeners(wrapper);
    attachRowLListeners(wrapper);
    attachRowFHListeners(wrapper);
    attachRowCListeners(wrapper);
    attachRowSListeners(wrapper);
    attachRowPListeners(wrapper);
  });
});
