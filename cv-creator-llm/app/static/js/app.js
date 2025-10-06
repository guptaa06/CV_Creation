// CV Creator LLM - Frontend JavaScript

let resumeUploaded = false;
let jobParsed = false;
let generatedFilename = null;

// DOM Elements
const resumeFile = document.getElementById('resume-file');
const uploadArea = document.getElementById('upload-area');
const resumeStatus = document.getElementById('resume-status');
const resumePreview = document.getElementById('resume-preview');

const jobDescription = document.getElementById('job-description');
const parseJobBtn = document.getElementById('parse-job-btn');
const jobStatus = document.getElementById('job-status');
const jobPreview = document.getElementById('job-preview');

const generateBtn = document.getElementById('generate-btn');
const generateStatus = document.getElementById('generate-status');
const formatSelect = document.getElementById('format-select');
const optimizationSelect = document.getElementById('optimization-select');

const downloadBtn = document.getElementById('download-btn');
const restartBtn = document.getElementById('restart-btn');

const loadingOverlay = document.getElementById('loading-overlay');

const parsingModelSelect = document.getElementById('parsing-model-select');
const generationModelSelect = document.getElementById('generation-model-select');
const refreshModelsBtn = document.getElementById('refresh-models-btn');
const parsingModelStatus = document.getElementById('parsing-model-status');
const generationModelStatus = document.getElementById('generation-model-status');

const editSummary = document.getElementById('edit-summary');
const editSkills = document.getElementById('edit-skills');
const editExperienceContainer = document.getElementById('edit-experience-container');
const recompareBtn = document.getElementById('recompare-btn');

let currentResumeData = null;
let selectedParsingModel = '';
let selectedGenerationModel = '';

// Utility Functions
function showLoading(text = 'Processing...') {
    loadingOverlay.querySelector('.loading-text').textContent = text;
    loadingOverlay.classList.remove('hidden');
}

function hideLoading() {
    loadingOverlay.classList.add('hidden');
}

function showStatus(element, message, type = 'info') {
    element.textContent = message;
    element.className = `status-message ${type}`;
}

function activateStep(stepNumber) {
    document.querySelectorAll('.step').forEach((step, index) => {
        if (index < stepNumber) {
            step.classList.add('active');
        }
    });
}

function showSection(sectionId) {
    document.getElementById(sectionId).classList.remove('hidden');
}

// File Upload
resumeFile.addEventListener('change', async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);

    showLoading('Extracting resume data...');

    try {
        const response = await fetch('/api/upload-resume', {
            method: 'POST',
            body: formData
        });

        const result = await response.json();

        if (result.success) {
            resumeUploaded = true;
            showStatus(resumeStatus, `✅ ${result.message}`, 'success');

            // Show preview
            resumePreview.innerHTML = `
                <h4>Resume Extracted</h4>
                <p><strong>Name:</strong> ${result.data.personal_info.name}</p>
                <p><strong>Email:</strong> ${result.data.personal_info.email || 'N/A'}</p>
                <p><strong>Skills:</strong> ${result.data.skills.slice(0, 5).join(', ')}...</p>
                <p><strong>Experience Entries:</strong> ${result.data.experience.length}</p>
            `;
            resumePreview.classList.remove('hidden');

            // Activate next step
            activateStep(2);
            showSection('job-section');
        } else {
            showStatus(resumeStatus, `❌ Error: ${result.detail || 'Upload failed'}`, 'error');
        }
    } catch (error) {
        showStatus(resumeStatus, `❌ Error: ${error.message}`, 'error');
    } finally {
        hideLoading();
    }
});

// Drag and drop
uploadArea.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadArea.style.background = '#dfe6e9';
});

uploadArea.addEventListener('dragleave', () => {
    uploadArea.style.background = '';
});

uploadArea.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadArea.style.background = '';

    const file = e.dataTransfer.files[0];
    if (file) {
        resumeFile.files = e.dataTransfer.files;
        resumeFile.dispatchEvent(new Event('change'));
    }
});

// Parse Job Description
parseJobBtn.addEventListener('click', async () => {
    const jobDesc = jobDescription.value.trim();

    if (!jobDesc) {
        showStatus(jobStatus, '❌ Please enter a job description', 'error');
        return;
    }

    showLoading('Parsing job description...');

    const formData = new FormData();
    formData.append('job_description', jobDesc);

    try {
        const response = await fetch('/api/parse-job', {
            method: 'POST',
            body: formData
        });

        const result = await response.json();

        if (result.success) {
            jobParsed = true;
            showStatus(jobStatus, `✅ ${result.message}`, 'success');

            // Show preview
            jobPreview.innerHTML = `
                <h4>Job Requirements Extracted</h4>
                <p><strong>Job Title:</strong> ${result.data.job_title}</p>
                <p><strong>Required Skills:</strong> ${result.data.required_skills.slice(0, 5).join(', ')}...</p>
                <p><strong>Total Keywords:</strong> ${result.data.keywords.length}</p>
            `;
            jobPreview.classList.remove('hidden');

            // Activate next step
            activateStep(3);
            showSection('generate-section');
        } else {
            showStatus(jobStatus, `❌ Error: ${result.detail || 'Parsing failed'}`, 'error');
        }
    } catch (error) {
        showStatus(jobStatus, `❌ Error: ${error.message}`, 'error');
    } finally {
        hideLoading();
    }
});

// Generate Resume
generateBtn.addEventListener('click', async () => {
    if (!resumeUploaded || !jobParsed) {
        showStatus(generateStatus, '❌ Please complete previous steps first', 'error');
        return;
    }

    showLoading('Tailoring your resume... This may take a minute.');

    const requestData = {
        job_description: jobDescription.value,
        target_format: formatSelect.value,
        optimization_level: optimizationSelect.value,
        include_summary: true
    };

    try {
        const response = await fetch('/api/generate-resume', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(requestData)
        });

        const result = await response.json();

        if (result.success) {
            showStatus(generateStatus, `✅ ${result.message}`, 'success');

            // Store filename for download
            generatedFilename = result.file_path.split(/[/\\]/).pop();

            // Display results
            displayResults(result);

            // Show results section
            showSection('results-section');
        } else {
            showStatus(generateStatus, `❌ Error: ${result.detail || 'Generation failed'}`, 'error');
        }
    } catch (error) {
        showStatus(generateStatus, `❌ Error: ${error.message}`, 'error');
    } finally {
        hideLoading();
    }
});

// Display Results
async function displayResults(result) {
    const atsAnalysis = result.ats_analysis;
    const evaluation = result.metadata.evaluation;

    // Fetch and display comparison data
    try {
        const comparisonResponse = await fetch('/api/comparison');
        const comparison = await comparisonResponse.json();

        // Update before/after score tiles
        updateScoreTile('ats-score', comparison.before.overall_score, comparison.after.overall_score, 'ats-improvement');
        updateScoreTile('keyword-score', comparison.before.keyword_match_score, comparison.after.keyword_match_score, 'keyword-improvement');
        updateScoreTile('quality-score', comparison.before.overall_quality, comparison.after.overall_quality, 'quality-improvement');

        displayComparison(comparison);
    } catch (error) {
        console.error('Error fetching comparison:', error);
    }

    // Matched keywords
    const matchedList = document.getElementById('matched-list');
    matchedList.innerHTML = '';
    atsAnalysis.matched_keywords.slice(0, 20).forEach(keyword => {
        const tag = document.createElement('span');
        tag.className = 'keyword-tag';
        tag.textContent = keyword;
        matchedList.appendChild(tag);
    });

    // Missing keywords
    const missingList = document.getElementById('missing-list');
    missingList.innerHTML = '';
    atsAnalysis.missing_keywords.slice(0, 10).forEach(keyword => {
        const tag = document.createElement('span');
        tag.className = 'keyword-tag';
        tag.textContent = keyword;
        missingList.appendChild(tag);
    });

    // Recommendations
    const recList = document.getElementById('recommendations-list');
    recList.innerHTML = '';
    evaluation.recommendations.forEach(rec => {
        const li = document.createElement('li');
        li.textContent = rec;
        recList.appendChild(li);
    });

    // Populate editable fields
    populateEditableFields(result);
}

function displayComparison(comparison) {
    // Before stats
    document.getElementById('before-skills').textContent = comparison.before.skills_count;
    document.getElementById('before-keywords').textContent = comparison.before.keyword_matches;
    document.getElementById('before-score').textContent = (comparison.before.keyword_match_score * 100).toFixed(0) + '%';

    // After stats
    document.getElementById('after-skills').textContent = comparison.after.skills_count;
    document.getElementById('after-keywords').textContent = comparison.after.keyword_matches;
    document.getElementById('after-score').textContent = (comparison.after.keyword_match_score * 100).toFixed(0) + '%';

    // Improvement banner
    const improvement = comparison.changes.improvement;
    let improvementText = '';

    if (improvement.percentage_improvement > 0) {
        improvementText = `🎉 Improved by ${improvement.percentage_improvement}%! Added ${improvement.keyword_count_increase} new keyword matches.`;
    } else if (improvement.percentage_improvement === 0) {
        improvementText = `✅ Maintained high quality with optimized structure.`;
    } else {
        improvementText = `📊 Resume optimized for better ATS compatibility.`;
    }

    document.getElementById('improvement-text').textContent = improvementText;

    // Skills added
    const skillsAddedList = document.getElementById('skills-added');
    skillsAddedList.innerHTML = '';
    if (comparison.changes.skills_added.length > 0) {
        comparison.changes.skills_added.forEach(skill => {
            const tag = document.createElement('span');
            tag.className = 'keyword-tag';
            tag.textContent = skill;
            skillsAddedList.appendChild(tag);
        });
    } else {
        skillsAddedList.innerHTML = '<p style="color: #95a5a6;">No new skills added</p>';
    }

    // New keywords matched
    const newKeywordsList = document.getElementById('new-keywords');
    newKeywordsList.innerHTML = '';
    if (comparison.changes.new_keywords_matched.length > 0) {
        comparison.changes.new_keywords_matched.forEach(keyword => {
            const tag = document.createElement('span');
            tag.className = 'keyword-tag';
            tag.textContent = keyword;
            newKeywordsList.appendChild(tag);
        });
    } else {
        newKeywordsList.innerHTML = '<p style="color: #95a5a6;">All keywords already matched</p>';
    }

    // Customizations made
    const customizationsList = document.getElementById('customizations-list');
    customizationsList.innerHTML = '';
    comparison.customizations.forEach(customization => {
        const li = document.createElement('li');
        li.textContent = customization;
        customizationsList.appendChild(li);
    });
}

function updateScore(elementId, score) {
    const scoreDisplay = document.getElementById(elementId);
    const scoreFill = document.getElementById(elementId + '-fill');

    const percentage = Math.round(score * 100);
    scoreDisplay.textContent = percentage + '%';
    scoreFill.style.width = percentage + '%';
}

function updateScoreTile(baseName, beforeScore, afterScore, improvementElementId) {
    // Update before score
    updateScore(baseName + '-before', beforeScore);

    // Update after score
    updateScore(baseName + '-after', afterScore);

    // Calculate and display improvement
    const improvementPercent = ((afterScore - beforeScore) * 100).toFixed(1);
    const improvementElement = document.getElementById(improvementElementId);

    if (improvementPercent > 0) {
        improvementElement.textContent = `+${improvementPercent}% improvement`;
        improvementElement.className = 'result-improvement positive';
    } else if (improvementPercent < 0) {
        improvementElement.textContent = `${improvementPercent}% change`;
        improvementElement.className = 'result-improvement negative';
    } else {
        improvementElement.textContent = 'No change';
        improvementElement.className = 'result-improvement neutral';
    }
}

// Download Resume
downloadBtn.addEventListener('click', () => {
    if (generatedFilename) {
        window.location.href = `/api/download/${generatedFilename}`;
    }
});

// Restart
restartBtn.addEventListener('click', async () => {
    if (confirm('Are you sure you want to start over?')) {
        showLoading('Resetting...');

        try {
            await fetch('/api/reset', { method: 'POST' });

            // Reset UI
            resumeUploaded = false;
            jobParsed = false;
            generatedFilename = null;

            resumeFile.value = '';
            jobDescription.value = '';

            resumeStatus.className = 'status-message';
            jobStatus.className = 'status-message';
            generateStatus.className = 'status-message';

            resumePreview.classList.add('hidden');
            jobPreview.classList.add('hidden');

            document.getElementById('job-section').classList.add('hidden');
            document.getElementById('generate-section').classList.add('hidden');
            document.getElementById('results-section').classList.add('hidden');

            document.querySelectorAll('.step').forEach((step, index) => {
                if (index === 0) {
                    step.classList.add('active');
                } else {
                    step.classList.remove('active');
                }
            });

            window.scrollTo(0, 0);
        } catch (error) {
            console.error('Reset error:', error);
        } finally {
            hideLoading();
        }
    }
});

// Check session status on load
async function checkSessionStatus() {
    try {
        const response = await fetch('/api/session-status');
        const status = await response.json();

        if (status.resume_uploaded) {
            resumeUploaded = true;
            showSection('job-section');
            activateStep(2);
        }

        if (status.job_parsed) {
            jobParsed = true;
            showSection('generate-section');
            activateStep(3);
        }
    } catch (error) {
        console.error('Status check error:', error);
    }
}

// Model Selection
async function loadAvailableModels() {
    try {
        const response = await fetch('/api/models');
        const data = await response.json();

        if (data.success && data.models.length > 0) {
            // Clear both dropdowns
            parsingModelSelect.innerHTML = '';
            generationModelSelect.innerHTML = '';

            data.models.forEach(model => {
                // Create option for parsing model
                const parsingOption = document.createElement('option');
                parsingOption.value = model.name;
                parsingOption.textContent = `${model.name} (${formatBytes(model.size)})`;

                // Create option for generation model
                const generationOption = document.createElement('option');
                generationOption.value = model.name;
                generationOption.textContent = `${model.name} (${formatBytes(model.size)})`;

                // Select current models from backend
                if (model.name === data.current_parsing_model) {
                    parsingOption.selected = true;
                    selectedParsingModel = model.name;
                }

                if (model.name === data.current_generation_model) {
                    generationOption.selected = true;
                    selectedGenerationModel = model.name;
                }

                parsingModelSelect.appendChild(parsingOption);
                generationModelSelect.appendChild(generationOption);
            });

            parsingModelStatus.textContent = '✓ Ready';
            parsingModelStatus.style.background = 'rgba(46, 204, 113, 0.3)';
            generationModelStatus.textContent = '✓ Ready';
            generationModelStatus.style.background = 'rgba(46, 204, 113, 0.3)';
        } else {
            parsingModelSelect.innerHTML = '<option value="">No models found</option>';
            generationModelSelect.innerHTML = '<option value="">No models found</option>';
            parsingModelStatus.textContent = '⚠ No models';
            parsingModelStatus.style.background = 'rgba(243, 156, 18, 0.3)';
            generationModelStatus.textContent = '⚠ No models';
            generationModelStatus.style.background = 'rgba(243, 156, 18, 0.3)';
        }
    } catch (error) {
        console.error('Error loading models:', error);
        parsingModelSelect.innerHTML = '<option value="">Error loading models</option>';
        generationModelSelect.innerHTML = '<option value="">Error loading models</option>';
        parsingModelStatus.textContent = '✗ Error';
        parsingModelStatus.style.background = 'rgba(231, 76, 60, 0.3)';
        generationModelStatus.textContent = '✗ Error';
        generationModelStatus.style.background = 'rgba(231, 76, 60, 0.3)';
    }
}

function formatBytes(bytes) {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 10) / 10 + ' ' + sizes[i];
}

// Parsing Model selection change
parsingModelSelect.addEventListener('change', async () => {
    selectedParsingModel = parsingModelSelect.value;
    parsingModelStatus.textContent = '⏳ Updating...';
    parsingModelStatus.style.background = 'rgba(52, 152, 219, 0.3)';

    try {
        const formData = new FormData();
        formData.append('model_name', selectedParsingModel);
        formData.append('model_type', 'parsing');

        const response = await fetch('/api/select-model', {
            method: 'POST',
            body: formData
        });

        const result = await response.json();

        if (result.success) {
            parsingModelStatus.textContent = '✓ Updated';
            parsingModelStatus.style.background = 'rgba(46, 204, 113, 0.3)';

            setTimeout(() => {
                parsingModelStatus.textContent = '✓ Ready';
            }, 1500);
        } else {
            throw new Error(result.message || 'Failed to update model');
        }
    } catch (error) {
        console.error('Error updating parsing model:', error);
        parsingModelStatus.textContent = '✗ Failed';
        parsingModelStatus.style.background = 'rgba(231, 76, 60, 0.3)';
    }
});

// Generation Model selection change
generationModelSelect.addEventListener('change', async () => {
    selectedGenerationModel = generationModelSelect.value;
    generationModelStatus.textContent = '⏳ Updating...';
    generationModelStatus.style.background = 'rgba(52, 152, 219, 0.3)';

    try {
        const formData = new FormData();
        formData.append('model_name', selectedGenerationModel);
        formData.append('model_type', 'generation');

        const response = await fetch('/api/select-model', {
            method: 'POST',
            body: formData
        });

        const result = await response.json();

        if (result.success) {
            generationModelStatus.textContent = '✓ Updated';
            generationModelStatus.style.background = 'rgba(46, 204, 113, 0.3)';

            setTimeout(() => {
                generationModelStatus.textContent = '✓ Ready';
            }, 1500);
        } else {
            throw new Error(result.message || 'Failed to update model');
        }
    } catch (error) {
        console.error('Error updating generation model:', error);
        generationModelStatus.textContent = '✗ Failed';
        generationModelStatus.style.background = 'rgba(231, 76, 60, 0.3)';
    }
});

// Refresh models button
refreshModelsBtn.addEventListener('click', async () => {
    refreshModelsBtn.style.pointerEvents = 'none';
    await loadAvailableModels();
    setTimeout(() => {
        refreshModelsBtn.style.pointerEvents = 'auto';
    }, 1000);
});

// Populate Editable Resume Fields
async function populateEditableFields(result) {
    try {
        // Fetch full resume data from the new endpoint
        const resumeDataResponse = await fetch('/api/resume-data');
        const resumeData = await resumeDataResponse.json();

        if (!resumeData.success) {
            console.error('Failed to fetch resume data');
            return;
        }

        const data = resumeData.data;

        // Format resume as plain text document
        let resumeText = '';

        // Contact Information
        resumeText += `${data.personal_info.name || ''}\n`;
        if (data.personal_info.email) resumeText += `${data.personal_info.email} `;
        if (data.personal_info.phone) resumeText += `| ${data.personal_info.phone} `;
        if (data.personal_info.location) resumeText += `| ${data.personal_info.location}`;
        resumeText += '\n';
        if (data.personal_info.linkedin) resumeText += `LinkedIn: ${data.personal_info.linkedin}\n`;
        if (data.personal_info.github) resumeText += `GitHub: ${data.personal_info.github}\n`;
        resumeText += '\n';

        // Professional Summary
        if (data.summary) {
            resumeText += 'PROFESSIONAL SUMMARY\n';
            resumeText += '─'.repeat(50) + '\n';
            resumeText += data.summary + '\n\n';
        }

        // Skills
        if (data.skills && data.skills.length > 0) {
            resumeText += 'SKILLS\n';
            resumeText += '─'.repeat(50) + '\n';
            resumeText += data.skills.join(', ') + '\n\n';
        }

        // Work Experience
        if (data.experience && data.experience.length > 0) {
            resumeText += 'WORK EXPERIENCE\n';
            resumeText += '─'.repeat(50) + '\n';
            data.experience.forEach((exp, index) => {
                resumeText += `\n${exp.position || ''} at ${exp.company || ''}\n`;
                if (exp.start_date || exp.end_date) {
                    resumeText += `${exp.start_date || ''} - ${exp.end_date || 'Present'}\n`;
                }
                if (exp.responsibilities && exp.responsibilities.length > 0) {
                    exp.responsibilities.forEach(resp => {
                        resumeText += `• ${resp}\n`;
                    });
                }
                if (index < data.experience.length - 1) resumeText += '\n';
            });
            resumeText += '\n';
        }

        // Education
        if (data.education && data.education.length > 0) {
            resumeText += 'EDUCATION\n';
            resumeText += '─'.repeat(50) + '\n';
            data.education.forEach((edu, index) => {
                resumeText += `\n${edu.degree || ''} - ${edu.institution || ''}\n`;
                if (edu.field_of_study) resumeText += `Field: ${edu.field_of_study}\n`;
                if (edu.end_date) resumeText += `Graduated: ${edu.end_date}\n`;
                if (edu.gpa) resumeText += `GPA: ${edu.gpa}\n`;
                if (index < data.education.length - 1) resumeText += '\n';
            });
            resumeText += '\n';
        }

        // Projects
        if (data.projects && data.projects.length > 0) {
            resumeText += 'PROJECTS\n';
            resumeText += '─'.repeat(50) + '\n';
            data.projects.forEach((proj, index) => {
                resumeText += `\n${proj.name || ''}\n`;
                if (proj.description) resumeText += `${proj.description}\n`;
                if (proj.technologies && proj.technologies.length > 0) {
                    resumeText += `Technologies: ${proj.technologies.join(', ')}\n`;
                }
                if (index < data.projects.length - 1) resumeText += '\n';
            });
        }

        // Populate the textarea
        document.getElementById('resume-content').value = resumeText.trim();

        // Store data for recompare
        currentResumeData = data;

    } catch (error) {
        console.error('Error populating fields:', error);
    }
}

function populateExperienceFields(experiences) {
    const container = document.getElementById('edit-experience-container');
    container.innerHTML = '';

    if (!experiences || experiences.length === 0) {
        container.innerHTML = '<p style="color: #95a5a6; font-style: italic; padding: 10px;">Your work experience will appear here for editing.</p>';
        return;
    }

    experiences.forEach((exp, index) => {
        const expDiv = document.createElement('div');
        expDiv.className = 'experience-item';
        expDiv.innerHTML = `
            <h4>Position ${index + 1}</h4>
            <input type="text" placeholder="Job Title" value="${exp.position || ''}" data-exp-index="${index}" data-field="position">
            <input type="text" placeholder="Company" value="${exp.company || ''}" data-exp-index="${index}" data-field="company">
            <div class="item-dates">
                <input type="text" placeholder="Start Date" value="${exp.start_date || ''}" data-exp-index="${index}" data-field="start_date">
                <input type="text" placeholder="End Date (or Present)" value="${exp.end_date || 'Present'}" data-exp-index="${index}" data-field="end_date">
            </div>
            <textarea placeholder="• Responsibility 1&#10;• Responsibility 2&#10;• Responsibility 3" data-exp-index="${index}">${(exp.responsibilities || []).map(r => `• ${r}`).join('\n')}</textarea>
        `;
        container.appendChild(expDiv);
    });
}

function populateEducationFields(education) {
    const container = document.getElementById('edit-education-container');
    container.innerHTML = '';

    if (!education || education.length === 0) {
        container.innerHTML = '<p style="color: #95a5a6; font-style: italic; padding: 10px;">Your education details will appear here for editing.</p>';
        return;
    }

    education.forEach((edu, index) => {
        const eduDiv = document.createElement('div');
        eduDiv.className = 'education-item';
        eduDiv.innerHTML = `
            <h4>Education ${index + 1}</h4>
            <input type="text" placeholder="Degree" value="${edu.degree || ''}" data-edu-index="${index}" data-field="degree">
            <input type="text" placeholder="Institution" value="${edu.institution || ''}" data-edu-index="${index}" data-field="institution">
            <input type="text" placeholder="Field of Study" value="${edu.field_of_study || ''}" data-edu-index="${index}" data-field="field_of_study">
            <div class="item-dates">
                <input type="text" placeholder="Start Date" value="${edu.start_date || ''}" data-edu-index="${index}" data-field="start_date">
                <input type="text" placeholder="End Date" value="${edu.end_date || ''}" data-edu-index="${index}" data-field="end_date">
            </div>
            <input type="text" placeholder="GPA (optional)" value="${edu.gpa || ''}" data-edu-index="${index}" data-field="gpa">
        `;
        container.appendChild(eduDiv);
    });
}

function populateProjectsFields(projects) {
    const container = document.getElementById('edit-projects-container');
    container.innerHTML = '';

    if (!projects || projects.length === 0) {
        container.innerHTML = '<p style="color: #95a5a6; font-style: italic; padding: 10px;">Your projects will appear here for editing.</p>';
        return;
    }

    projects.forEach((proj, index) => {
        const projDiv = document.createElement('div');
        projDiv.className = 'project-item';
        projDiv.innerHTML = `
            <h4>Project ${index + 1}</h4>
            <input type="text" placeholder="Project Name" value="${proj.name || ''}" data-proj-index="${index}" data-field="name">
            <textarea placeholder="Project description and key achievements..." data-proj-index="${index}" data-field="description">${proj.description || ''}</textarea>
            <input type="text" placeholder="Technologies (comma-separated)" value="${(proj.technologies || []).join(', ')}" data-proj-index="${index}" data-field="technologies">
        `;
        container.appendChild(projDiv);
    });
}

// Parse resume text to extract structured data
function parseResumeText(text) {
    const lines = text.split('\n');
    const data = {
        summary: '',
        skills: [],
        experience: []
    };

    let currentSection = '';
    let currentExp = null;

    for (let i = 0; i < lines.length; i++) {
        const line = lines[i].trim();

        if (line.includes('PROFESSIONAL SUMMARY')) {
            currentSection = 'summary';
            i++; // Skip separator line
            continue;
        } else if (line.includes('SKILLS')) {
            currentSection = 'skills';
            i++; // Skip separator line
            continue;
        } else if (line.includes('WORK EXPERIENCE')) {
            currentSection = 'experience';
            i++; // Skip separator line
            continue;
        } else if (line.includes('EDUCATION') || line.includes('PROJECTS')) {
            currentSection = 'other';
            continue;
        }

        // Process based on current section
        if (currentSection === 'summary' && line && !line.startsWith('─')) {
            data.summary += line + ' ';
        } else if (currentSection === 'skills' && line && !line.startsWith('─')) {
            const skills = line.split(',').map(s => s.trim()).filter(s => s);
            data.skills.push(...skills);
        } else if (currentSection === 'experience') {
            if (line.startsWith('•')) {
                // Responsibility
                if (currentExp) {
                    currentExp.responsibilities.push(line.substring(1).trim());
                }
            } else if (line && !line.startsWith('─')) {
                // Could be a new position or date line
                if (line.includes(' at ')) {
                    // New position
                    if (currentExp) {
                        data.experience.push(currentExp);
                    }
                    currentExp = {
                        responsibilities: []
                    };
                }
            }
        }
    }

    // Add last experience if exists
    if (currentExp && currentExp.responsibilities.length > 0) {
        data.experience.push(currentExp);
    }

    data.summary = data.summary.trim();

    return data;
}

// Recompare Button Handler
recompareBtn.addEventListener('click', async () => {
    showLoading('Recalculating analysis...');

    try {
        // Get the edited resume text
        const resumeContent = document.getElementById('resume-content').value;

        // Parse the resume text to extract data
        const parsedData = parseResumeText(resumeContent);

        // Send to backend
        const response = await fetch('/api/recompare', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(parsedData)
        });

        const result = await response.json();

        if (result.success) {
            // Update filename for download
            generatedFilename = result.file_path.split(/[/\\]/).pop();

            // Refresh comparison
            const comparisonResponse = await fetch('/api/comparison');
            const comparison = await comparisonResponse.json();

            // Update score tiles
            updateScoreTile('ats-score', comparison.before.overall_score, comparison.after.overall_score, 'ats-improvement');
            updateScoreTile('keyword-score', comparison.before.keyword_match_score, comparison.after.keyword_match_score, 'keyword-improvement');
            updateScoreTile('quality-score', comparison.before.overall_quality, comparison.after.overall_quality, 'quality-improvement');

            // Update comparison section
            displayComparison(comparison);

            // Update detailed analysis
            const matchedList = document.getElementById('matched-list');
            matchedList.innerHTML = '';
            result.ats_analysis.matched_keywords.slice(0, 20).forEach(keyword => {
                const tag = document.createElement('span');
                tag.className = 'keyword-tag';
                tag.textContent = keyword;
                matchedList.appendChild(tag);
            });

            const missingList = document.getElementById('missing-list');
            missingList.innerHTML = '';
            result.ats_analysis.missing_keywords.slice(0, 10).forEach(keyword => {
                const tag = document.createElement('span');
                tag.className = 'keyword-tag';
                tag.textContent = keyword;
                missingList.appendChild(tag);
            });

            // Show success message
            alert('✅ Resume recalculated successfully! Download the updated version.');

        } else {
            alert('❌ Error: ' + (result.detail || 'Recompare failed'));
        }

    } catch (error) {
        console.error('Recompare error:', error);
        alert('❌ Error: ' + error.message);
    } finally {
        hideLoading();
    }
});

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    loadAvailableModels();
    checkSessionStatus();
});
