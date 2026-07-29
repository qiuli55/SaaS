<template>
  <div class="privacy-page">
    <div class="page-header"><h1 class="page-title">数据安全说明</h1></div>
    <div class="privacy-card">
      <div class="section">
        <div class="section-icon">🗄️</div>
        <div class="section-body">
          <h3>数据存储在你自己的服务器上</h3>
          <p>本系统部署在你自有的云服务器中，客户数据（姓名、电话、身份证号、案件材料）全部存储在你控制的数据库里。运营方无法远程访问你的服务器或数据库。</p>
        </div>
      </div>
      <div class="section">
        <div class="section-icon">🔒</div>
        <div class="section-body">
          <h3>数据隔离</h3>
          <p>每个账号只能查看自己创建的客户、案件和文书。不同律师所之间的数据完全隔离，同一律所内的多名律师也需要分别登录。</p>
        </div>
      </div>
      <div class="section">
        <div class="section-icon">🤖</div>
        <div class="section-body">
          <h3>AI 文书生成仅发送案情文本</h3>
          <p>当你使用文书生成功能时，只有案由、事实描述、诉讼请求等文本会发送给 AI。当事人的姓名、电话、身份证号、微信等个人信息<b>不会</b>发送给第三方。</p>
        </div>
      </div>
      <div class="section">
        <div class="section-icon">🧑‍⚖️</div>
        <div class="section-body">
          <h3>符合律师执业规范</h3>
          <p>系统设计时考虑了律师保密义务要求。你可以选择是否关闭 AI 功能，关闭后系统仍可正常用于案件管理、客户管理和文书编辑。</p>
        </div>
      </div>
      <div class="section">
        <div class="section-icon">📋</div>
        <div class="section-body">
          <h3>第三方服务</h3>
          <p>文书生成功能依赖 DeepSeek API。DeepSeek 承诺不会使用用户数据训练模型，传输使用 HTTPS 加密。</p>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.privacy-page { max-width: 720px; margin: 0 auto }
.privacy-card {
  background: var(--color-background-secondary);
  border: 1px solid var(--color-border-tertiary);
  border-radius: 12px;
  padding: 32px;
}
.section {
  display: flex;
  gap: 16px;
  padding: 20px 0;
  border-bottom: 1px solid var(--color-border-tertiary);
}
.section:first-child { padding-top: 0 }
.section:last-child { border-bottom: none; padding-bottom: 0 }
.section-icon { font-size: 28px; flex-shrink: 0; line-height: 1.4 }
.section-body h3 { font-size: 15px; font-weight: 500; color: var(--text-primary); margin: 0 0 6px }
.section-body p { font-size: 13px; color: var(--text-secondary); line-height: 1.7; margin: 0 }
</style>
