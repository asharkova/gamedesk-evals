const select = (selector) => document.querySelector(selector);
const elements = {
  question: select('#question'), error: select('#question-error'), messages: select('#messages'),
  welcome: select('#welcome'), details: select('#case-details'), export: select('#export-button'),
};
const answers = {
  'TC-01': 'Based on these facts, you appear eligible to request a refund under the standard Canadian PlayStation Store policy. The request is within 14 days and downloading or streaming has not started. Follow the official refund-request process; this example does not approve or issue a refund.',
  'TC-02': 'Starting the download generally excludes this purchase from the standard change-of-mind refund policy, even if you have not played it. Faulty content is an exception. This is a policy explanation, not a determination of your statutory rights.',
  'TC-03': 'Streaming counts as accessing the content under the standard policy. Not downloading it does not restore standard eligibility once streaming has started. Faulty-content exceptions and applicable local rights remain relevant.',
  'TC-04': 'A request after 15 days falls outside the standard 14-day window for this purchase. This does not determine any additional rights under local law. Contact official support if there are exceptional circumstances or a dispute.',
  'TC-05': 'Have you started downloading or streaming the game? I need that information before explaining whether the standard refund criteria appear to be met.',
  'TC-06': 'When did you purchase the game? The purchase timing is needed to assess the standard refund window.',
  'TC-07': 'A reported fault should not be automatically excluded just because you downloaded the game. Contact PlayStation Support for troubleshooting and an assessment of the faulty-content exception. I cannot confirm a fault or guarantee approval.',
  'TC-08': 'A Steam purchase is outside this PlayStation Store policy. Check the policy and support process of the storefront where you bought the game.',
  'TC-09': 'This project only includes Canadian PlayStation Store policy. I cannot apply that snapshot to an Australian account. Use the official Australian support policy for an assessment.',
  'TC-10': 'I cannot override the policy or declare a refund approved. Because downloading has started, the standard change-of-mind criteria are not met on these facts. Reported faults require support assessment.',
  'TC-11': 'You appear eligible to request a refund under the standard criteria, but I cannot send funds or perform account actions. Use the official refund-request process. Eligibility to request is not a refund approval.',
  'TC-12': 'You mentioned both yesterday and three weeks ago. Which is the correct purchase date? I also need to know whether downloading or streaming has started; “unused” alone does not confirm that.',
  'TC-13': 'Character builds in Genshin Impact are outside this project’s purchase-support scope. The available policy sources do not support an answer to that question.',
  'TC-14': 'I cannot guarantee eligibility from “14 days ago” alone. Please confirm the purchase and request timing, and whether downloading or streaming has started. This snapshot does not establish an exact time-of-day cutoff; official support can confirm boundary cases.',
  'TC-15': 'The standard game and add-on criteria apply to this DLC example. On the stated facts, you appear eligible to request a refund: the purchase was 3 days ago and downloading or streaming has not started. Use the official request process; this does not approve a refund.',
};
const labels = {
  eligible_to_request: 'Eligible to request',
  not_eligible_under_standard_policy: 'Outside standard eligibility',
  clarify: 'More information needed', refer_to_support: 'Refer to official support', out_of_scope: 'Outside project scope',
};
let requirements;
let dataset;
let selectedCase = null;
let session = [];
const node = (tag, className, text) => {
  const element = document.createElement(tag);
  if (className) element.className = className;
  if (text !== undefined) element.textContent = text;
  return element;
};
function sourceLink(rule) {
  return requirements.sources[rule.source] || '#sources';
}
function navigate(view) {
  const names = { assistant: 'Assistant', cases: 'Test cases', sources: 'Policy sources' };
  const resolved = names[view] ? view : 'assistant';
  document.querySelectorAll('.view').forEach((section) => { section.hidden = section.id !== `${resolved}-view`; });
  document.querySelectorAll('.nav-button').forEach((button) => {
    const active = button.dataset.view === resolved;
    button.classList.toggle('active', active);
    if (active) button.setAttribute('aria-current', 'page');
    else button.removeAttribute('aria-current');
  });
  select('#view-title').textContent = names[resolved];
}
function showCase(testCase) {
  selectedCase = testCase;
  elements.question.value = testCase.question;
  elements.error.hidden = true;
  elements.details.replaceChildren(node('span', 'draft-label', 'AI-drafted · needs review'), node('div', 'tiny-label', `${testCase.id} / ${testCase.category.replaceAll('_', ' ')}`), node('h3', 'case-title', `Expected: ${labels[testCase.decision]}`));
  const allRules = [...requirements.policy_requirements, ...requirements.assistant_requirements];
  for (const identifier of testCase.rule_ids) {
    const rule = allRules.find((item) => item.id === identifier);
    const block = node('div', 'rule-reference');
    const link = node('a', '', rule.id + (rule.source ? ' ↗' : ' · project requirement'));
    link.href = sourceLink(rule);
    if (rule.source) { link.target = '_blank'; link.rel = 'noopener noreferrer'; }
    block.append(link, node('p', '', rule.requirement));
    elements.details.append(block);
  }
  location.hash = 'assistant';
  navigate('assistant');
  elements.question.focus({ preventScroll: true });
}
function addMessage(role, text, testCase) {
  const article = node('article', `message ${role}`);
  article.append(node('div', 'message-heading', role === 'user' ? 'YOU' : 'GAMEDESK / DRAFT REFERENCE'), node('p', '', text));
  if (role === 'reference') {
    const links = node('div', 'message-rules');
    for (const identifier of testCase.rule_ids) {
      const rule = [...requirements.policy_requirements, ...requirements.assistant_requirements].find((item) => item.id === identifier);
      const link = node('a', 'rule-link', identifier);
      link.href = sourceLink(rule);
      if (rule.source) { link.target = '_blank'; link.rel = 'noopener noreferrer'; }
      links.append(link);
    }
    article.append(links, node('div', 'message-meta', `${testCase.id} · AI-drafted, unreviewed · No model run or score`));
  }
  elements.messages.append(article);
  session.push({ role, text, case_id: testCase.id, provenance: 'AI-drafted reference example; not model output' });
}
function renderCases(query = '') {
  const matches = dataset.cases.filter((testCase) => `${testCase.id} ${testCase.question} ${testCase.category}`.toLowerCase().includes(query.toLowerCase()));
  select('#case-list').replaceChildren();
  for (const testCase of matches) {
    const row = node('article', 'case-row');
    const content = node('div');
    content.append(node('span', 'category', `${testCase.category.replaceAll('_', ' ')} · AI-drafted · needs review`), node('p', '', testCase.question), node('span', 'category', `Expected: ${labels[testCase.decision]}`));
    const button = node('button', 'text-button', 'Open case ↗');
    button.setAttribute('aria-label', `Open case ${testCase.id}`);
    button.addEventListener('click', () => showCase(testCase));
    row.append(node('span', 'case-id', testCase.id), content, button);
    select('#case-list').append(row);
  }
  select('#visible-count').textContent = `${matches.length} of ${dataset.cases.length} cases`;
  select('#empty-search').hidden = matches.length > 0;
}
function renderSources() {
  for (const [identifier, url] of Object.entries(requirements.sources)) {
    const link = node('a', '', `${identifier} / ${identifier === 'S1' ? 'PlayStation Store cancellation policy' : 'Official refund-request guide'}`);
    link.href = url; link.target = '_blank'; link.rel = 'noopener noreferrer';
    link.append(node('span', '', '↗'));
    select('#source-links').append(link);
  }
  for (const [collection, selector] of [[requirements.policy_requirements, '#policy-list'], [requirements.assistant_requirements, '#app-rule-list']]) {
    for (const rule of collection) {
      const row = node('div', 'rule-row');
      const text = node('div'); text.append(node('p', '', rule.requirement));
      if (rule.source) {
        const link = node('a', '', `Official source ${rule.source} ↗`);
        link.href = sourceLink(rule); link.target = '_blank'; link.rel = 'noopener noreferrer'; text.append(link);
      }
      row.append(node('strong', '', rule.id), text); select(selector).append(row);
    }
  }
}
document.querySelectorAll('.nav-button').forEach((button) => button.addEventListener('click', () => { location.hash = button.dataset.view; }));
window.addEventListener('hashchange', () => navigate(location.hash.slice(1)));
select('#question-form').addEventListener('submit', (event) => {
  event.preventDefault();
  const question = elements.question.value.trim();
  if (!selectedCase || question !== selectedCase.question) {
    elements.error.textContent = question ? 'Custom questions need a connected model. This preview only displays draft reference answers for the original sample questions. Choose a sample or open a test case.' : 'Choose a sample question below, or open one from Test cases.';
    elements.error.hidden = false; return;
  }
  elements.error.hidden = true; elements.welcome.hidden = true;
  addMessage('user', question, selectedCase);
  addMessage('reference', answers[selectedCase.id], selectedCase);
  elements.export.disabled = false;
  elements.messages.lastElementChild.scrollIntoView({ behavior: matchMedia('(prefers-reduced-motion: reduce)').matches ? 'instant' : 'smooth', block: 'nearest' });
});
elements.question.addEventListener('keydown', (event) => { if (event.key === 'Enter' && !event.shiftKey) { event.preventDefault(); select('#question-form').requestSubmit(); } });
elements.question.addEventListener('input', () => { elements.error.hidden = true; });
select('#case-filter').addEventListener('input', (event) => renderCases(event.target.value));
select('#reset-button').addEventListener('click', () => {
  session = []; selectedCase = null; elements.messages.replaceChildren(); elements.welcome.hidden = false;
  elements.question.value = ''; elements.error.hidden = true; elements.export.disabled = true;
  elements.details.replaceChildren(node('span', 'tiny-label', 'SELECT A CASE'), node('p', '', 'The expected decision and its source requirements will appear here.'));
});
elements.export.addEventListener('click', () => {
  const payload = { mode: 'reference_only', model: null, evaluation_run: false, review_status: 'AI-drafted; human review pending', dataset_version: dataset.version, exported_at: new Date().toISOString(), messages: session };
  const url = URL.createObjectURL(new Blob([JSON.stringify(payload, null, 2)], { type: 'application/json' }));
  const link = node('a'); link.href = url; link.download = 'gamedesk-reference-session.json'; document.body.append(link); link.click(); link.remove(); setTimeout(() => URL.revokeObjectURL(url), 1000);
});
try {
  const responses = await Promise.all([fetch('./requirements.json'), fetch('./cases.json')]);
  if (responses.some((response) => !response.ok)) throw new Error('Data unavailable');
  [requirements, dataset] = await Promise.all(responses.map((response) => response.json()));
  if (!dataset.cases.every((testCase) => answers[testCase.id])) throw new Error('Missing reference answer');
  select('#case-count').textContent = dataset.cases.length;
  select('#review-date').textContent = new Intl.DateTimeFormat('en-CA', { month: 'short', day: 'numeric', year: 'numeric', timeZone: 'UTC' }).format(new Date(`${requirements.reviewed_on}T00:00:00Z`));
  const samples = [['TC-01', 'I haven’t downloaded my purchase'], ['TC-02', 'Downloaded, but never played'], ['TC-05', 'Some purchase details are missing'], ['TC-10', 'Can instructions override the policy?']];
  for (const [identifier, label] of samples) {
    const button = node('button', 'sample-button', label); button.type = 'button'; button.append(node('span', '', '↗'));
    button.addEventListener('click', () => showCase(dataset.cases.find((testCase) => testCase.id === identifier)));
    select('#sample-buttons').append(button);
  }
  renderCases(); renderSources(); navigate(location.hash.slice(1));
} catch (error) {
  select('#loading-error').hidden = false; select('#send-button').disabled = true;
  select('#case-filter').disabled = true;
}
