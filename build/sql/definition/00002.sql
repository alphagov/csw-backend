--
-- Name: severity; Type: TABLE; Schema: public; Owner: cloud_sec_watch
--

CREATE TABLE IF NOT EXISTS public.severity (
    id SERIAL NOT NULL PRIMARY KEY,
    severity_name character varying(255) NOT NULL,
    description text NOT NULL
);

ALTER TABLE public.severity OWNER TO cloud_sec_watch;

--
-- Name: status; Type: TABLE; Schema: public; Owner: cloud_sec_watch
--

CREATE TABLE IF NOT EXISTS public.status (
    id SERIAL NOT NULL PRIMARY KEY,
    status_name character varying(255) NOT NULL,
    description text NOT NULL
);

ALTER TABLE public.status OWNER TO cloud_sec_watch;

--
-- Name: user; Type: TABLE; Schema: public; Owner: cloud_sec_watch
--

CREATE TABLE IF NOT EXISTS public."user" (
    id SERIAL NOT NULL PRIMARY KEY,
    email character varying(255) NOT NULL,
    name character varying(255) NOT NULL,
    active boolean NOT NULL
);

ALTER TABLE public."user" OWNER TO cloud_sec_watch;

--
-- Name: user_session; Type: TABLE; Schema: public; Owner: cloud_sec_watch
--

CREATE TABLE IF NOT EXISTS public.user_session (
    id SERIAL NOT NULL PRIMARY KEY,
    date_opened timestamp without time zone NOT NULL,
    date_accessed timestamp without time zone NOT NULL,
    date_closed timestamp without time zone,
    user_id integer NOT NULL REFERENCES public."user"(id)
);

ALTER TABLE public.user_session OWNER TO cloud_sec_watch;

--
-- Name: product_team; Type: TABLE; Schema: public; Owner: cloud_sec_watch
--

CREATE TABLE IF NOT EXISTS public.product_team (
    id SERIAL NOT NULL PRIMARY KEY,
    team_name character varying(255) NOT NULL,
    active boolean NOT NULL
);

ALTER TABLE public.product_team OWNER TO cloud_sec_watch;

--
-- Name: product_team_user; Type: TABLE; Schema: public; Owner: cloud_sec_watch
--

CREATE TABLE IF NOT EXISTS public.product_team_user (
    id SERIAL NOT NULL PRIMARY KEY,
    user_id integer NOT NULL REFERENCES public."user"(id),
    team_id integer NOT NULL REFERENCES public.product_team(id)
);

ALTER TABLE public.product_team_user OWNER TO cloud_sec_watch;

--
-- Name: account_subscription; Type: TABLE; Schema: public; Owner: cloud_sec_watch
--

CREATE TABLE IF NOT EXISTS public.account_subscription (
    id SERIAL NOT NULL PRIMARY KEY,
    account_id bigint NOT NULL,
    account_name character varying(255) NOT NULL,
    product_team_id integer NOT NULL REFERENCES public.product_team(id),
    active boolean NOT NULL
);

ALTER TABLE public.account_subscription OWNER TO cloud_sec_watch;

--
-- Name: account_audit; Type: TABLE; Schema: public; Owner: cloud_sec_watch
--

CREATE TABLE IF NOT EXISTS public.account_audit (
    id SERIAL NOT NULL PRIMARY KEY,
    account_subscription_id integer NOT NULL REFERENCES public.account_subscription(id),
    date_started timestamp without time zone NOT NULL,
    date_updated timestamp without time zone NOT NULL,
    date_completed timestamp without time zone,
    active_criteria integer NOT NULL,
    criteria_processed integer NOT NULL,
    criteria_passed integer NOT NULL,
    criteria_failed integer NOT NULL,
    issues_found integer NOT NULL
);

ALTER TABLE public.account_audit OWNER TO cloud_sec_watch;

--
-- Name: account_latest_audit; Type: TABLE; Schema: public; Owner: cloud_sec_watch
--

CREATE TABLE IF NOT EXISTS public.account_latest_audit (
    id SERIAL NOT NULL PRIMARY KEY,
    account_subscription_id integer NOT NULL REFERENCES public.account_subscription(id),
    account_audit_id integer NOT NULL REFERENCES public.account_audit(id)
);

ALTER TABLE public.account_latest_audit OWNER TO cloud_sec_watch;

--
-- Name: criteria_provider; Type: TABLE; Schema: public; Owner: cloud_sec_watch
--

CREATE TABLE IF NOT EXISTS public.criteria_provider (
    id SERIAL NOT NULL PRIMARY KEY,
    provider_name character varying(255) NOT NULL
);


ALTER TABLE public.criteria_provider OWNER TO cloud_sec_watch;

--
-- Name: criterion; Type: TABLE; Schema: public; Owner: cloud_sec_watch
--

CREATE TABLE IF NOT EXISTS public.criterion (
    id SERIAL NOT NULL PRIMARY KEY,
    criterion_name character varying(255) NOT NULL,
    criteria_provider_id integer NOT NULL REFERENCES public.criteria_provider(id),
    invoke_class_name character varying(255) NOT NULL,
    invoke_class_get_data_method character varying(255) NOT NULL,
    title text NOT NULL,
    description text NOT NULL,
    why_is_it_important text NOT NULL,
    how_do_i_fix_it text NOT NULL,
    active boolean NOT NULL,
    is_regional boolean NOT NULL
);

ALTER TABLE public.criterion OWNER TO cloud_sec_watch;

--
-- Name: audit_criterion; Type: TABLE; Schema: public; Owner: cloud_sec_watch
--

CREATE TABLE IF NOT EXISTS public.audit_criterion (
    id SERIAL NOT NULL PRIMARY KEY,
    criterion_id integer NOT NULL REFERENCES public.criterion(id),
    account_audit_id integer NOT NULL REFERENCES public.account_audit(id),
    regions integer NOT NULL,
    resources integer NOT NULL,
    tested integer NOT NULL,
    passed integer NOT NULL,
    failed integer NOT NULL,
    ignored integer NOT NULL
);

ALTER TABLE public.audit_criterion OWNER TO cloud_sec_watch;

--
-- Name: audit_resource; Type: TABLE; Schema: public; Owner: cloud_sec_watch
--

CREATE TABLE IF NOT EXISTS public.audit_resource (
    id SERIAL NOT NULL PRIMARY KEY,
    criterion_id integer NOT NULL REFERENCES public.criterion(id),
    account_audit_id integer NOT NULL REFERENCES public.account_audit(id),
    region character varying(255),
    resource_id character varying(255) NOT NULL,
    resource_name character varying(255),
    resource_data text NOT NULL,
    date_evaluated timestamp without time zone NOT NULL
);

ALTER TABLE public.audit_resource OWNER TO cloud_sec_watch;

--
-- Name: criterion_params; Type: TABLE; Schema: public; Owner: cloud_sec_watch
--

CREATE TABLE IF NOT EXISTS public.criterion_params (
    id SERIAL NOT NULL PRIMARY KEY,
    criterion_id integer NOT NULL REFERENCES public.criterion(id),
    param_name character varying(255) NOT NULL,
    param_value character varying(255) NOT NULL
);

ALTER TABLE public.criterion_params OWNER TO cloud_sec_watch;

--
-- Name: resource_compliance; Type: TABLE; Schema: public; Owner: cloud_sec_watch
--

CREATE TABLE IF NOT EXISTS public.resource_compliance (
    id SERIAL NOT NULL PRIMARY KEY,
    audit_resource_id integer NOT NULL REFERENCES public.audit_resource(id),
    annotation text,
    resource_type character varying(255) NOT NULL,
    resource_id character varying(255) NOT NULL,
    compliance_type character varying(255) NOT NULL,
    is_compliant boolean NOT NULL,
    is_applicable boolean NOT NULL,
    status_id integer NOT NULL
);

ALTER TABLE public.resource_compliance OWNER TO cloud_sec_watch;

--
-- Name: resource_risk_assessment; Type: TABLE; Schema: public; Owner: cloud_sec_watch
--

CREATE TABLE IF NOT EXISTS public.resource_risk_assessment (
    id SERIAL NOT NULL PRIMARY KEY,
    criterion_id integer NOT NULL REFERENCES public.criterion(id),
    audit_resource_id integer NOT NULL REFERENCES public.audit_resource(id),
    account_audit_id integer NOT NULL REFERENCES public.account_audit(id),
    resource_id character varying(255) NOT NULL,
    date_first_identifed date NOT NULL,
    date_last_notified date,
    date_of_review date,
    accepted_risk boolean NOT NULL,
    analyst_assessed boolean NOT NULL,
    severity_id integer
);

ALTER TABLE public.resource_risk_assessment OWNER TO cloud_sec_watch;

--
-- Insert status data
--

INSERT INTO public.status (status_name, description)
VALUES
('Unknown', 'Not yet evaluated'),
('Pass', 'Compliant or not-applicable'),
('Fail', 'Non-compliant')
ON CONFLICT DO NOTHING;

--
-- Insert provider data
--

INSERT INTO public.criteria_provider (provider_name)
VALUES
('AWS Trusted Advisor'),
('AWS Elastic Cloud Compute (EC2) service'),
('AWS Identity and Access Management (IAM) service')
ON CONFLICT DO NOTHING;
