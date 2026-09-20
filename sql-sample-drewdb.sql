CREATE TABLE IF NOT EXISTS "user" (
	"id" UUID NOT NULL,
	"name" VARCHAR(150) NOT NULL,
	"email" VARCHAR(255) NOT NULL,
	"location" VARCHAR(150),
	"create_at" TIMESTAMP NOT NULL,
	PRIMARY KEY("id")
);

CREATE TABLE IF NOT EXISTS "Opportunity" (
	"id" UUID NOT NULL,
	"organization_id" UUID NOT NULL,
	"title" VARCHAR(500) NOT NULL,
	"description" TEXT,
	"type" VARCHAR(50) NOT NULL,
	"url" TEXT NOT NULL,
	"deadline" DATE,
	"posted_at" TIMESTAMP,
	"created_at" TIMESTAMP,
	PRIMARY KEY("id")
);

CREATE TABLE IF NOT EXISTS "Organization" (
	"id" UUID NOT NULL,
	"name" VARCHAR(150) NOT NULL,
	"type" VARCHAR(50) NOT NULL,
	"country" VARCHAR(150) NOT NULL,
	"city" VARCHAR(150) NOT NULL,
	"website" TEXT NOT NULL,
	PRIMARY KEY("id")
);

CREATE TABLE IF NOT EXISTS "Researcher" (
	"id" UUID NOT NULL,
	"organization_id" UUID NOT NULL,
	"department_id" UUID NOT NULL,
	"name" VARCHAR(255) NOT NULL,
	"position" VARCHAR(150) NOT NULL,
	"email" VARCHAR(255),
	"profile_url" TEXT NOT NULL,
	"orcid" VARCHAR(50),
	PRIMARY KEY("id")
);

CREATE TABLE IF NOT EXISTS "Publication" (
	"id" UUID NOT NULL,
	"title" TEXT NOT NULL,
	"abstract" TEXT NOT NULL,
	"year" INTEGER NOT NULL,
	"doi" VARCHAR(255) NOT NULL,
	"journal" VARCHAR(255) NOT NULL,
	"url" TEXT NOT NULL,
	PRIMARY KEY("id")
);

CREATE TABLE IF NOT EXISTS "Education" (
	"id" UUID NOT NULL,
	"user_id" UUID NOT NULL,
	"institution_id" UUID NOT NULL,
	"degree" VARCHAR(150) NOT NULL,
	"field" VARCHAR(200) NOT NULL,
	"gpa" DECIMAL(4,2) NOT NULL,
	"start_date" DATE,
	"end_date" DATE,
	PRIMARY KEY("id")
);

CREATE TABLE IF NOT EXISTS "Experience" (
	"id" UUID NOT NULL,
	"user_id" UUID NOT NULL,
	"organization_id" UUID NOT NULL,
	"title" VARCHAR(255) NOT NULL,
	"description" TEXT,
	"start_date" DATE,
	"end_date" DATE,
	PRIMARY KEY("id")
);

CREATE TABLE IF NOT EXISTS "Department" (
	"id" UUID NOT NULL,
	"organization_id" UUID NOT NULL,
	"name" VARCHAR(255) NOT NULL,
	"description" TEXT,
	PRIMARY KEY("id")
);

CREATE TABLE IF NOT EXISTS "ResearchGroup" (
	"id" UUID NOT NULL,
	"department_id" UUID NOT NULL,
	"name" VARCHAR(255) NOT NULL,
	"description" TEXT,
	"website" TEXT,
	PRIMARY KEY("id")
);

CREATE TABLE IF NOT EXISTS "ResearchInterest" (
	"id" UUID NOT NULL,
	"name" VARCHAR(255) NOT NULL,
	"description" TEXT,
	PRIMARY KEY("id")
);

CREATE TABLE IF NOT EXISTS "Skill" (
	"id" UUID NOT NULL,
	"name" VARCHAR(150) NOT NULL,
	"category" VARCHAR(150),
	PRIMARY KEY("id")
);

CREATE TABLE IF NOT EXISTS "Language" (
	"id" UUID NOT NULL,
	"name" VARCHAR(150) NOT NULL,
	"code" VARCHAR(15) NOT NULL,
	PRIMARY KEY("id")
);

CREATE TABLE IF NOT EXISTS "UserSkill" (
	"user_id" UUID NOT NULL,
	"skill_id" UUID NOT NULL,
	"level" VARCHAR(255) NOT NULL
);

CREATE TABLE IF NOT EXISTS "UserLanguage" (
	"user_id" UUID NOT NULL,
	"language_id" UUID NOT NULL,
	"level" VARCHAR(255) NOT NULL
);

CREATE TABLE IF NOT EXISTS "OpportunitySkill" (
	"opportunity_id" UUID NOT NULL,
	"skill_id" UUID NOT NULL,
	"required" VARCHAR(255) NOT NULL
);

CREATE TABLE IF NOT EXISTS "OpportunityLanguage" (
	"opportunity_id" UUID NOT NULL,
	"language_id" UUID NOT NULL,
	"minimum_level" VARCHAR(255) NOT NULL
);

CREATE TABLE IF NOT EXISTS "ResearcherPublication" (
	"researcher_id" UUID NOT NULL,
	"publication_id" UUID NOT NULL,
	"author_order" VARCHAR(255) NOT NULL
);

CREATE TABLE IF NOT EXISTS "ResearcherInterest" (
	"researcher_id" UUID NOT NULL,
	"interest_id" UUID NOT NULL
);

CREATE TABLE IF NOT EXISTS "UserResearchInterest" (
	"user_id" UUID NOT NULL,
	"interest_id" UUID NOT NULL
);

CREATE TABLE IF NOT EXISTS "ResearchGroupMember" (
	"research_group_id" UUID NOT NULL,
	"researcher_id" UUID NOT NULL,
	"role" VARCHAR(255) NOT NULL
);

ALTER TABLE "Opportunity"
ADD FOREIGN KEY("organization_id") REFERENCES "Organization"("id")
ON UPDATE NO ACTION ON DELETE NO ACTION;
ALTER TABLE "Researcher"
ADD FOREIGN KEY("organization_id") REFERENCES "Organization"("id")
ON UPDATE NO ACTION ON DELETE NO ACTION;
ALTER TABLE "Education"
ADD FOREIGN KEY("user_id") REFERENCES "user"("id")
ON UPDATE NO ACTION ON DELETE NO ACTION;
ALTER TABLE "Experience"
ADD FOREIGN KEY("user_id") REFERENCES "user"("id")
ON UPDATE NO ACTION ON DELETE NO ACTION;
ALTER TABLE "Experience"
ADD FOREIGN KEY("organization_id") REFERENCES "Organization"("id")
ON UPDATE NO ACTION ON DELETE NO ACTION;
ALTER TABLE "Department"
ADD FOREIGN KEY("organization_id") REFERENCES "Organization"("id")
ON UPDATE NO ACTION ON DELETE NO ACTION;
ALTER TABLE "ResearchGroup"
ADD FOREIGN KEY("department_id") REFERENCES "Department"("id")
ON UPDATE NO ACTION ON DELETE NO ACTION;
ALTER TABLE "Researcher"
ADD FOREIGN KEY("department_id") REFERENCES "Department"("id")
ON UPDATE NO ACTION ON DELETE NO ACTION;
ALTER TABLE "Education"
ADD FOREIGN KEY("institution_id") REFERENCES "Organization"("id")
ON UPDATE NO ACTION ON DELETE NO ACTION;
ALTER TABLE "Researcher"
ADD FOREIGN KEY("department_id") REFERENCES "Department"("id")
ON UPDATE NO ACTION ON DELETE NO ACTION;
ALTER TABLE "UserSkill"
ADD FOREIGN KEY("user_id") REFERENCES "user"("id")
ON UPDATE NO ACTION ON DELETE NO ACTION;
ALTER TABLE "UserSkill"
ADD FOREIGN KEY("skill_id") REFERENCES "Skill"("id")
ON UPDATE NO ACTION ON DELETE NO ACTION;
ALTER TABLE "UserLanguage"
ADD FOREIGN KEY("user_id") REFERENCES "user"("id")
ON UPDATE NO ACTION ON DELETE NO ACTION;
ALTER TABLE "UserLanguage"
ADD FOREIGN KEY("language_id") REFERENCES "Language"("id")
ON UPDATE NO ACTION ON DELETE NO ACTION;
ALTER TABLE "OpportunitySkill"
ADD FOREIGN KEY("opportunity_id") REFERENCES "Opportunity"("id")
ON UPDATE NO ACTION ON DELETE NO ACTION;
ALTER TABLE "OpportunitySkill"
ADD FOREIGN KEY("skill_id") REFERENCES "Skill"("id")
ON UPDATE NO ACTION ON DELETE NO ACTION;
ALTER TABLE "OpportunityLanguage"
ADD FOREIGN KEY("opportunity_id") REFERENCES "Opportunity"("id")
ON UPDATE NO ACTION ON DELETE NO ACTION;
ALTER TABLE "OpportunityLanguage"
ADD FOREIGN KEY("language_id") REFERENCES "Language"("id")
ON UPDATE NO ACTION ON DELETE NO ACTION;
ALTER TABLE "ResearcherPublication"
ADD FOREIGN KEY("researcher_id") REFERENCES "Researcher"("id")
ON UPDATE NO ACTION ON DELETE NO ACTION;
ALTER TABLE "ResearcherPublication"
ADD FOREIGN KEY("publication_id") REFERENCES "Publication"("id")
ON UPDATE NO ACTION ON DELETE NO ACTION;
ALTER TABLE "ResearcherInterest"
ADD FOREIGN KEY("researcher_id") REFERENCES "Researcher"("id")
ON UPDATE NO ACTION ON DELETE NO ACTION;
ALTER TABLE "ResearcherInterest"
ADD FOREIGN KEY("interest_id") REFERENCES "ResearchInterest"("id")
ON UPDATE NO ACTION ON DELETE NO ACTION;
ALTER TABLE "UserResearchInterest"
ADD FOREIGN KEY("interest_id") REFERENCES "ResearchInterest"("id")
ON UPDATE NO ACTION ON DELETE NO ACTION;
ALTER TABLE "UserResearchInterest"
ADD FOREIGN KEY("user_id") REFERENCES "user"("id")
ON UPDATE NO ACTION ON DELETE NO ACTION;
ALTER TABLE "ResearchGroupMember"
ADD FOREIGN KEY("research_group_id") REFERENCES "ResearchGroup"("id")
ON UPDATE NO ACTION ON DELETE NO ACTION;
ALTER TABLE "ResearchGroupMember"
ADD FOREIGN KEY("researcher_id") REFERENCES "Researcher"("id")
ON UPDATE NO ACTION ON DELETE NO ACTION;